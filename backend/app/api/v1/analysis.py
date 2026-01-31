import logging
from typing import List
from uuid import UUID
import pandas as pd
from fastapi import APIRouter, HTTPException

from app.models.analysis import (
    AnalysisRequest,
    AnalysisResponse,
    AnalysisResult,
    InsightItem,
    ChartConfig
)
from app.services.ai_analyzer import AIAnalyzer
from app.services.insight_generator import InsightGenerator
from app.core.database import get_supabase

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/analysis/generate", response_model=AnalysisResponse)
async def generate_analysis(request: AnalysisRequest):
    """
    Generate AI-powered analysis for a processed file.

    Args:
        request: AnalysisRequest with file_id and analysis_types

    Returns:
        AnalysisResponse with generated insights and chart configurations
    """
    try:
        supabase = get_supabase()
        
        # Step 1: Validate file exists and is completed
        file_response = supabase.table("files").select("*").eq("id", str(request.file_id)).execute()
        
        if not file_response.data or len(file_response.data) == 0:
            raise HTTPException(status_code=404, detail="File not found")
        
        file_data = file_response.data[0]
        
        if file_data.get("status") != "completed":
            raise HTTPException(
                status_code=400,
                detail=f"File must be in 'completed' status. Current status: {file_data.get('status')}"
            )
        
        # Step 2: Retrieve processed_data
        processed_response = supabase.table("processed_data").select("*").eq(
            "file_id", str(request.file_id)
        ).execute()
        
        if not processed_response.data or len(processed_response.data) == 0:
            raise HTTPException(
                status_code=400,
                detail="No processed data available for this file"
            )
        
        processed_data = processed_response.data[0]
        cleaned_data = processed_data.get("cleaned_data")
        data_schema = processed_data.get("data_schema", {})
        
        if not cleaned_data:
            raise HTTPException(
                status_code=400,
                detail="File has no cleaned data available"
            )
        
        # Step 3: Convert cleaned_data to DataFrame
        try:
            df = pd.DataFrame(cleaned_data)
        except Exception as e:
            logger.error(f"Failed to create DataFrame: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail="Failed to process cleaned data into DataFrame"
            )
        
        # Step 4: Initialize services
        analyzer = AIAnalyzer()
        generator = InsightGenerator()
        
        # Step 5: Perform analysis for each requested type
        results = []
        
        for analysis_type in request.analysis_types:
            try:
                # Call appropriate analyzer method
                if analysis_type == "trend":
                    raw_output = analyzer.analyze_trends(df, data_schema)
                elif analysis_type == "anomaly":
                    raw_output = analyzer.detect_anomalies(df, data_schema)
                elif analysis_type == "executive_summary":
                    file_metadata = {
                        "name": file_data.get("filename"),
                        "size": file_data.get("file_size"),
                        "upload_date": file_data.get("created_at")
                    }
                    raw_output = analyzer.generate_executive_summary(
                        df, data_schema, file_metadata
                    )
                else:
                    logger.warning(f"Unknown analysis type: {analysis_type}")
                    continue
                
                # Validate and convert insights
                insights = generator.validate_insights(raw_output)
                
                # Generate chart config if chart data is present
                chart_config = None
                if "chart_data" in raw_output and raw_output["chart_data"]:
                    recommended_chart = raw_output.get("recommended_chart", "bar")
                    chart_type = generator.select_chart_type(
                        raw_output["chart_data"],
                        analysis_type,
                        recommended_chart
                    )
                    chart_config = generator.generate_chart_config(
                        chart_type=chart_type,
                        data=raw_output["chart_data"],
                        schema=data_schema,
                        title=f"{analysis_type.replace('_', ' ').title()} Analysis",
                        description=f"AI-generated {analysis_type} insights"
                    )
                    chart_config = generator.apply_professional_styling(chart_config)
                
                # Enrich metadata
                metadata = generator.enrich_metadata(insights, raw_output, analysis_type)
                
                # Prepare data for database insertion
                analysis_data = {
                    "file_id": str(request.file_id),
                    "analysis_type": analysis_type,
                    "insights": [insight.model_dump() for insight in insights],
                    "chart_config": chart_config.model_dump() if chart_config else None,
                    "anomalies": raw_output.get("anomalies"),
                    "key_metrics": raw_output.get("key_metrics"),
                    "recommendations": raw_output.get("recommendations"),
                    "metadata": metadata
                }
                
                # Step 6: Insert into analysis_results table
                insert_response = supabase.table("analysis_results").insert(
                    analysis_data
                ).execute()
                
                if insert_response.data and len(insert_response.data) > 0:
                    db_result = insert_response.data[0]
                    
                    # Create AnalysisResult model
                    result = AnalysisResult(
                        id=db_result["id"],
                        file_id=UUID(db_result["file_id"]),
                        analysis_type=db_result["analysis_type"],
                        insights=insights,
                        chart_config=chart_config,
                        metadata=db_result.get("metadata", {}),
                        created_at=db_result["created_at"]
                    )
                    results.append(result)
                
            except Exception as e:
                logger.error(f"Error processing {analysis_type} analysis: {str(e)}")
                # Insert error result into database
                error_data = {
                    "file_id": str(request.file_id),
                    "analysis_type": analysis_type,
                    "insights": [{
                        "title": "Analisi fallita",
                        "description": f"Errore durante l'elaborazione: {str(e)}",
                        "severity": "low"
                    }],
                    "chart_config": None,
                    "metadata": {
                        "error": str(e),
                        "status": "failed"
                    }
                }
                supabase.table("analysis_results").insert(error_data).execute()
        
        # Step 7: Retrieve all results for response
        final_response = supabase.table("analysis_results").select("*").eq(
            "file_id", str(request.file_id)
        ).order("created_at", desc=True).execute()
        
        all_results = []
        if final_response.data:
            for db_result in final_response.data:
                # Reconstruct models from database
                insights = [
                    InsightItem(**insight_data)
                    for insight_data in db_result.get("insights", [])
                ]
                
                chart_config = None
                if db_result.get("chart_config"):
                    chart_config = ChartConfig(**db_result["chart_config"])
                
                result = AnalysisResult(
                    id=db_result["id"],
                    file_id=UUID(db_result["file_id"]),
                    analysis_type=db_result["analysis_type"],
                    insights=insights,
                    chart_config=chart_config,
                    anomalies=db_result.get("anomalies"),
                    key_metrics=db_result.get("key_metrics"),
                    recommendations=db_result.get("recommendations"),
                    metadata=db_result.get("metadata", {}),
                    created_at=db_result["created_at"]
                )
                all_results.append(result)
        
        # Build response
        response = AnalysisResponse(
            file_id=request.file_id,
            results=all_results,
            message=f"Successfully generated {len(results)} analysis results"
        )
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in generate_analysis: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )
