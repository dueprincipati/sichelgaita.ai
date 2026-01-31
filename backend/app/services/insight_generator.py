import logging
from typing import Dict, List, Any, Optional
from app.models.analysis import InsightItem, ChartConfig

logger = logging.getLogger(__name__)

# Professional color palette (Investment Bank style)
PROFESSIONAL_COLORS = ["#1e40af", "#0f172a", "#475569", "#3b82f6", "#60a5fa"]


class InsightGenerator:
    """Service for post-processing and enriching AI-generated insights."""

    @staticmethod
    def validate_insights(raw_json: Dict) -> List[InsightItem]:
        """
        Validate and convert raw JSON to InsightItem models.

        Args:
            raw_json: Raw JSON output from AI analyzer

        Returns:
            List of validated InsightItem objects
        """
        insights = []
        raw_insights = raw_json.get("insights", [])

        for item in raw_insights:
            try:
                insight = InsightItem(
                    title=item.get("title", "Untitled Insight"),
                    description=item.get("description", "No description available"),
                    severity=item.get("severity", "medium"),
                    metric_value=item.get("metric_value"),
                    metric_label=item.get("metric_label")
                )
                insights.append(insight)
            except Exception as e:
                logger.warning(f"Failed to validate insight: {item}. Error: {str(e)}")
                # Add a placeholder insight for failed validation
                insights.append(InsightItem(
                    title="Insight non valido",
                    description="Impossibile processare questo insight",
                    severity="low"
                ))

        return insights

    @staticmethod
    def generate_chart_config(
        chart_type: str,
        data: List[Dict],
        schema: Dict,
        title: str = "Chart",
        description: Optional[str] = None
    ) -> ChartConfig:
        """
        Generate Recharts-compatible chart configuration.

        Args:
            chart_type: Type of chart (line, bar, pie, area)
            data: Chart data points
            schema: Data schema for axis selection
            title: Chart title
            description: Optional chart description

        Returns:
            ChartConfig object ready for frontend rendering
        """
        try:
            # Determine axes from data keys
            x_axis = None
            y_axis = None
            
            if data and len(data) > 0:
                keys = list(data[0].keys())
                if len(keys) >= 2:
                    x_axis = keys[0]
                    y_axis = keys[1]
                elif len(keys) == 1:
                    x_axis = keys[0]

            # Apply professional styling
            styled_config = ChartConfig(
                chart_type=chart_type if chart_type in ["line", "bar", "pie", "area"] else "bar",
                data=data,
                x_axis=x_axis,
                y_axis=y_axis,
                colors=PROFESSIONAL_COLORS,
                title=title,
                description=description
            )

            return styled_config

        except Exception as e:
            logger.error(f"Failed to generate chart config: {str(e)}")
            # Return minimal valid config
            return ChartConfig(
                chart_type="bar",
                data=[],
                title=title,
                description="Chart configuration error"
            )

    @staticmethod
    def apply_professional_styling(config: ChartConfig) -> ChartConfig:
        """
        Apply professional styling to chart configuration.

        Args:
            config: Base chart configuration

        Returns:
            ChartConfig with professional styling applied
        """
        # Override colors with professional palette
        config.colors = PROFESSIONAL_COLORS
        
        # Ensure title is capitalized
        config.title = config.title.title() if config.title else "Analysis Chart"
        
        return config

    @staticmethod
    def select_chart_type(data: List[Dict], analysis_type: str, recommended: Optional[str] = None) -> str:
        """
        Select appropriate chart type based on data characteristics.

        Args:
            data: Chart data points
            analysis_type: Type of analysis (trend, anomaly, executive_summary)
            recommended: AI-recommended chart type

        Returns:
            Chart type string (line, bar, pie, area)
        """
        # Use AI recommendation if valid
        if recommended in ["line", "bar", "pie", "area"]:
            return recommended

        # Fallback logic based on analysis type
        if analysis_type == "trend":
            return "line"
        elif analysis_type == "anomaly":
            return "bar"
        elif analysis_type == "executive_summary":
            return "bar"
        
        return "bar"  # Default

    @staticmethod
    def enrich_metadata(
        insights: List[InsightItem],
        raw_data: Dict,
        analysis_type: str
    ) -> Dict[str, Any]:
        """
        Enrich analysis metadata with quality indicators.

        Args:
            insights: List of insights
            raw_data: Raw analysis output
            analysis_type: Type of analysis performed

        Returns:
            Metadata dictionary
        """
        metadata = {
            "analysis_type": analysis_type,
            "insight_count": len(insights),
            "high_severity_count": sum(1 for i in insights if i.severity == "high"),
            "data_quality": "good",  # Can be enhanced with actual quality checks
            "has_recommendations": "recommendations" in raw_data,
            "has_chart_data": "chart_data" in raw_data or "anomalies" in raw_data
        }

        # Add confidence score based on insight count and severity
        confidence_score = 0.5  # Base score
        if metadata["insight_count"] > 0:
            confidence_score += 0.2
        if metadata["high_severity_count"] > 0:
            confidence_score += 0.3
        
        metadata["confidence_score"] = min(confidence_score, 1.0)

        return metadata
