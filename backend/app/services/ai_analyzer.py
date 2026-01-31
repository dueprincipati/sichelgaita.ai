import json
import logging
from typing import Dict, List, Any
import pandas as pd
import google.generativeai as genai

from app.core.config import settings

logger = logging.getLogger(__name__)


class AIAnalyzer:
    """AI-powered data analysis service using Gemini."""

    def __init__(self):
        """Initialize the AI analyzer with Gemini configuration."""
        genai.configure(api_key=settings.GEMINI_API_KEY)
        self.model = genai.GenerativeModel(settings.GEMINI_MODEL)
        self.generation_config = {
            "temperature": 0.2,
            "max_output_tokens": 2048,
        }

    def analyze_trends(self, df: pd.DataFrame, data_schema: Dict) -> Dict:
        """
        Analyze trends in the dataset.

        Args:
            df: DataFrame with processed data
            data_schema: Schema information from processed_data

        Returns:
            Dictionary with insights and chart configuration
        """
        try:
            # Limit sample data to reduce token usage
            sample_data = df.head(100).to_dict(orient='records')
            
            # Calculate basic statistics
            numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
            statistics = {}
            if numeric_cols:
                for col in numeric_cols:
                    statistics[col] = {
                        'mean': float(df[col].mean()),
                        'min': float(df[col].min()),
                        'max': float(df[col].max()),
                        'std': float(df[col].std()) if df[col].std() == df[col].std() else 0
                    }

            prompt = f"""Analizza questo dataset per identificare trend significativi.
Schema: {json.dumps(data_schema, indent=2)}
Statistiche: {json.dumps(statistics, indent=2)}
Dati campione (prime 100 righe): {json.dumps(sample_data[:10], indent=2)}

Restituisci SOLO un JSON valido con questa struttura esatta:
{{
  "insights": [
    {{
      "title": "Trend principale identificato",
      "description": "Descrizione dettagliata con numeri",
      "severity": "high",
      "metric_value": 123.45,
      "metric_label": "etichetta metrica"
    }}
  ],
  "chart_data": [
    {{"x": "periodo", "y": 100}}
  ],
  "recommended_chart": "line"
}}

Focus su: crescita/decrescita, stagionalità, punti di inflessione.
Usa severità: high per trend significativi, medium per pattern interessanti, low per osservazioni minori.
Non includere markdown o testo extra, solo JSON."""

            response = self.model.generate_content(
                prompt,
                generation_config=self.generation_config
            )

            # Parse JSON response
            result = self._parse_json_response(response.text)
            
            return result

        except Exception as e:
            logger.error(f"Error in trend analysis: {str(e)}")
            return {
                "insights": [{
                    "title": "Analisi non disponibile",
                    "description": f"Errore durante l'analisi: {str(e)}",
                    "severity": "low"
                }],
                "chart_data": [],
                "recommended_chart": "bar"
            }

    def detect_anomalies(self, df: pd.DataFrame, data_schema: Dict) -> Dict:
        """
        Detect anomalies and outliers in the dataset.

        Args:
            df: DataFrame with processed data
            data_schema: Schema information from processed_data

        Returns:
            Dictionary with anomaly insights and details
        """
        try:
            # Calculate statistics for anomaly detection
            numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
            statistics = {}
            anomalies_detected = []

            if numeric_cols:
                for col in numeric_cols:
                    mean = df[col].mean()
                    std = df[col].std()
                    
                    # Check if std is not NaN and greater than zero to avoid division by zero
                    if std == std and std > 0:
                        # Z-score based anomaly detection
                        z_scores = ((df[col] - mean) / std).abs()
                        outliers = df[z_scores > 3]
                        
                        statistics[col] = {
                            'mean': float(mean),
                            'std': float(std),
                            'outlier_count': len(outliers)
                        }
                        
                        if len(outliers) > 0:
                            anomalies_detected.append({
                                'column': col,
                                'count': len(outliers),
                                'max_zscore': float(z_scores.max())
                            })
                    elif std == std:
                        # Column has zero standard deviation (all values are the same)
                        statistics[col] = {
                            'mean': float(mean),
                            'std': 0.0,
                            'outlier_count': 0
                        }

            sample_data = df.head(100).to_dict(orient='records')

            prompt = f"""Identifica anomalie e outlier in questo dataset.
Schema: {json.dumps(data_schema, indent=2)}
Statistiche: {json.dumps(statistics, indent=2)}
Anomalie rilevate (Z-score > 3): {json.dumps(anomalies_detected, indent=2)}
Dati campione: {json.dumps(sample_data[:10], indent=2)}

Restituisci SOLO un JSON valido con questa struttura:
{{
  "insights": [
    {{
      "title": "Anomalia rilevata",
      "description": "Spiegazione dettagliata con contesto",
      "severity": "high",
      "metric_value": 456.78,
      "metric_label": "deviazione standard"
    }}
  ],
  "anomalies": [
    {{"index": 5, "value": 1000, "expected": 100}}
  ]
}}

Usa metodi statistici: Z-score, IQR, deviazione standard.
Severità: high per anomalie critiche, medium per outlier significativi, low per variazioni minori.
Non includere markdown o testo extra, solo JSON."""

            response = self.model.generate_content(
                prompt,
                generation_config=self.generation_config
            )

            result = self._parse_json_response(response.text)
            
            return result

        except Exception as e:
            logger.error(f"Error in anomaly detection: {str(e)}")
            return {
                "insights": [{
                    "title": "Analisi anomalie non disponibile",
                    "description": f"Errore durante il rilevamento: {str(e)}",
                    "severity": "low"
                }],
                "anomalies": []
            }

    def generate_executive_summary(
        self,
        df: pd.DataFrame,
        data_schema: Dict,
        file_metadata: Dict
    ) -> Dict:
        """
        Generate McKinsey-style executive summary.

        Args:
            df: DataFrame with processed data
            data_schema: Schema information from processed_data
            file_metadata: File metadata including name, size, etc.

        Returns:
            Dictionary with executive insights and recommendations
        """
        try:
            # Calculate key metrics
            numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
            key_metrics = {}
            
            if numeric_cols:
                for col in numeric_cols[:5]:  # Limit to top 5 numeric columns
                    key_metrics[col] = {
                        'total': float(df[col].sum()),
                        'average': float(df[col].mean()),
                        'max': float(df[col].max()),
                        'min': float(df[col].min())
                    }

            # Determine date range if date column exists
            date_cols = df.select_dtypes(include=['datetime64']).columns.tolist()
            date_range = "N/A"
            if date_cols and len(date_cols) > 0:
                date_col = date_cols[0]
                date_range = f"{df[date_col].min()} to {df[date_col].max()}"

            file_name = file_metadata.get('name', 'Unknown')
            sample_data = df.head(50).to_dict(orient='records')

            prompt = f"""Crea un executive summary professionale stile McKinsey.
Dataset: {file_name}
Schema: {json.dumps(data_schema, indent=2)}
Periodo: {date_range}
Righe totali: {len(df)}
Metriche chiave: {json.dumps(key_metrics, indent=2)}
Dati campione: {json.dumps(sample_data[:5], indent=2)}

Restituisci SOLO un JSON valido con questa struttura:
{{
  "insights": [
    {{
      "title": "Key Takeaway #1",
      "description": "So What? Implicazione business con numeri concreti",
      "severity": "high"
    }},
    {{
      "title": "Key Takeaway #2",
      "description": "Secondo insight rilevante",
      "severity": "medium"
    }}
  ],
  "key_metrics": [
    {{"label": "Metrica principale", "value": 12345, "change": "+15%"}},
    {{"label": "Seconda metrica", "value": 67890, "change": "-5%"}}
  ],
  "recommendations": [
    "Azione concreta #1 con impatto stimato",
    "Azione concreta #2 basata sui dati"
  ]
}}

Linguaggio: executive, quantitativo, orientato all'azione.
Struttura: Situazione → Complicazione → Risoluzione.
Focus su: insight strategici, implicazioni business, azioni concrete.
Non includere markdown o testo extra, solo JSON."""

            response = self.model.generate_content(
                prompt,
                generation_config=self.generation_config
            )

            result = self._parse_json_response(response.text)
            
            return result

        except Exception as e:
            logger.error(f"Error in executive summary generation: {str(e)}")
            return {
                "insights": [{
                    "title": "Executive Summary non disponibile",
                    "description": f"Errore durante la generazione: {str(e)}",
                    "severity": "low"
                }],
                "key_metrics": [],
                "recommendations": []
            }

    def _parse_json_response(self, text: str) -> Dict:
        """
        Parse JSON response from Gemini, handling markdown code blocks.

        Args:
            text: Raw text response from Gemini

        Returns:
            Parsed JSON dictionary
        """
        try:
            # Remove markdown code blocks if present
            text = text.strip()
            if text.startswith("```json"):
                text = text[7:]
            elif text.startswith("```"):
                text = text[3:]
            if text.endswith("```"):
                text = text[:-3]
            
            text = text.strip()
            
            # Parse JSON
            return json.loads(text)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {text}")
            logger.error(f"JSON error: {str(e)}")
            # Return minimal valid structure
            return {
                "insights": [{
                    "title": "Errore di parsing",
                    "description": "La risposta AI non è in formato JSON valido",
                    "severity": "low"
                }]
            }
