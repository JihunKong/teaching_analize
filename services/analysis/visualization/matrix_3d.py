"""
3D Matrix Visualization using Plotly
Interactive 3D heatmap for Stage × Context × Level analysis
"""

import logging
from typing import Dict, Any, List, Optional
import json

# Plotly for 3D visualization
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import numpy as np

logger = logging.getLogger(__name__)


class Matrix3DVisualizer:
    """Generate interactive 3D visualizations for teaching analysis matrices"""

    def __init__(self):
        """Initialize 3D visualizer with default settings"""
        self.color_scale = 'Viridis'  # Color scheme for heatmap
        self.stage_labels = ['Introduction', 'Development', 'Closing']
        self.context_labels = ['Explanation', 'Question', 'Feedback', 'Facilitation', 'Management']
        self.level_labels = ['L1', 'L2', 'L3']

    def generate_3d_heatmap(self, matrix_data: Dict[str, Any]) -> str:
        """
        Generate interactive 3D heatmap visualization

        Args:
            matrix_data: 3D matrix data from Module 2

        Returns:
            HTML string with embedded Plotly chart
        """
        try:
            logger.info("Generating 3D matrix heatmap")

            # Extract matrix
            matrix = matrix_data.get('matrix', {})

            if not matrix:
                logger.warning("No matrix data provided")
                return self._generate_empty_visualization()

            # Prepare 3D data
            x_coords, y_coords, z_coords, values, hover_texts = self._prepare_3d_data(matrix)

            # Create 3D scatter plot with cube visualization
            fig = go.Figure(data=[go.Scatter3d(
                x=x_coords,
                y=y_coords,
                z=z_coords,
                mode='markers',
                marker=dict(
                    size=values,
                    color=values,
                    colorscale=self.color_scale,
                    showscale=True,
                    colorbar=dict(
                        title="빈도",
                        thickness=20,
                        len=0.7
                    ),
                    line=dict(color='white', width=0.5),
                    sizemode='diameter',
                    sizeref=max(values) / 30 if values else 1,
                    opacity=0.8
                ),
                text=hover_texts,
                hovertemplate='%{text}<br>빈도: %{marker.size:.0f}<extra></extra>',
                name='3D Matrix'
            )])

            # Update layout
            fig.update_layout(
                title=dict(
                    text='3D 매트릭스 시각화 (Stage × Context × Level)',
                    font=dict(size=20, color='#2C3E50'),
                    x=0.5,
                    xanchor='center'
                ),
                scene=dict(
                    xaxis=dict(
                        title='Stage',
                        tickvals=[0, 1, 2],
                        ticktext=self.stage_labels,
                        backgroundcolor="rgb(240, 240, 240)",
                        gridcolor="white"
                    ),
                    yaxis=dict(
                        title='Context',
                        tickvals=[0, 1, 2, 3, 4],
                        ticktext=self.context_labels,
                        backgroundcolor="rgb(240, 240, 240)",
                        gridcolor="white"
                    ),
                    zaxis=dict(
                        title='Level',
                        tickvals=[0, 1, 2],
                        ticktext=self.level_labels,
                        backgroundcolor="rgb(240, 240, 240)",
                        gridcolor="white"
                    ),
                    camera=dict(
                        eye=dict(x=1.5, y=1.5, z=1.3)
                    )
                ),
                width=1000,
                height=700,
                margin=dict(l=0, r=0, t=50, b=0),
                hovermode='closest'
            )

            # Generate HTML
            html = self._generate_html_wrapper(fig)

            logger.info("3D heatmap generated successfully")
            return html

        except Exception as e:
            logger.error(f"3D heatmap generation failed: {str(e)}")
            return self._generate_error_visualization(str(e))

    def generate_2d_heatmaps(self, matrix_data: Dict[str, Any]) -> str:
        """
        Generate multiple 2D heatmaps (slices of 3D matrix)

        Args:
            matrix_data: 3D matrix data

        Returns:
            HTML string with subplot heatmaps
        """
        try:
            logger.info("Generating 2D heatmap slices")

            matrix = matrix_data.get('matrix', {})

            if not matrix:
                return self._generate_empty_visualization()

            # Create subplots for each cognitive level
            fig = make_subplots(
                rows=1, cols=3,
                subplot_titles=('L1 (기억/이해)', 'L2 (적용/분석)', 'L3 (종합/평가)'),
                horizontal_spacing=0.15,
                vertical_spacing=0.1
            )

            # Generate heatmap for each level
            for level_idx, level_name in enumerate(self.level_labels):
                z_data, x_labels, y_labels = self._prepare_2d_slice(matrix, level_idx)

                heatmap = go.Heatmap(
                    z=z_data,
                    x=x_labels,
                    y=y_labels,
                    colorscale=self.color_scale,
                    showscale=(level_idx == 2),  # Only show color scale on last plot
                    hovertemplate='%{y} - %{x}<br>빈도: %{z}<extra></extra>'
                )

                fig.add_trace(heatmap, row=1, col=level_idx + 1)

            # Update layout
            fig.update_layout(
                title=dict(
                    text='인지 수준별 2D 히트맵',
                    font=dict(size=18, color='#2C3E50'),
                    x=0.5,
                    xanchor='center'
                ),
                height=400,
                width=1200,
                margin=dict(l=100, r=50, t=80, b=80)
            )

            # Update axes
            for i in range(1, 4):
                fig.update_xaxes(title_text="Stage", row=1, col=i)
                fig.update_yaxes(title_text="Context", row=1, col=i)

            html = self._generate_html_wrapper(fig)

            logger.info("2D heatmap slices generated successfully")
            return html

        except Exception as e:
            logger.error(f"2D heatmap generation failed: {str(e)}")
            return self._generate_error_visualization(str(e))

    def generate_distribution_charts(self, matrix_data: Dict[str, Any]) -> str:
        """
        Generate distribution charts for Stage, Context, and Level

        Args:
            matrix_data: 3D matrix data with statistics

        Returns:
            HTML string with distribution charts
        """
        try:
            logger.info("Generating distribution charts")

            stats = matrix_data.get('statistics', {})

            if not stats:
                return self._generate_empty_visualization()

            # Create subplots
            fig = make_subplots(
                rows=1, cols=3,
                subplot_titles=('Stage 분포', 'Context 분포', 'Level 분포'),
                specs=[[{'type': 'bar'}, {'type': 'bar'}, {'type': 'bar'}]],
                horizontal_spacing=0.12
            )

            # Stage distribution
            stage_dist = stats.get('stage_distribution', {})
            stage_values = [
                stage_dist.get('introduction', {}).get('percentage', 0),
                stage_dist.get('development', {}).get('percentage', 0),
                stage_dist.get('closing', {}).get('percentage', 0)
            ]

            fig.add_trace(
                go.Bar(
                    x=self.stage_labels,
                    y=stage_values,
                    marker_color='#667eea',
                    text=[f'{v:.1f}%' for v in stage_values],
                    textposition='outside',
                    hovertemplate='%{x}<br>%{y:.1f}%<extra></extra>'
                ),
                row=1, col=1
            )

            # Context distribution
            context_dist = stats.get('context_distribution', {})
            context_values = [
                context_dist.get('explanation', {}).get('percentage', 0),
                context_dist.get('question', {}).get('percentage', 0),
                context_dist.get('feedback', {}).get('percentage', 0),
                context_dist.get('facilitation', {}).get('percentage', 0),
                context_dist.get('management', {}).get('percentage', 0)
            ]

            fig.add_trace(
                go.Bar(
                    x=self.context_labels,
                    y=context_values,
                    marker_color='#4BC0C0',
                    text=[f'{v:.1f}%' for v in context_values],
                    textposition='outside',
                    hovertemplate='%{x}<br>%{y:.1f}%<extra></extra>'
                ),
                row=1, col=2
            )

            # Level distribution
            level_dist = stats.get('level_distribution', {})
            level_values = [
                level_dist.get('l1', {}).get('percentage', 0),
                level_dist.get('l2', {}).get('percentage', 0),
                level_dist.get('l3', {}).get('percentage', 0)
            ]

            fig.add_trace(
                go.Bar(
                    x=self.level_labels,
                    y=level_values,
                    marker_color='#FF6384',
                    text=[f'{v:.1f}%' for v in level_values],
                    textposition='outside',
                    hovertemplate='%{x}<br>%{y:.1f}%<extra></extra>'
                ),
                row=1, col=3
            )

            # Update layout
            fig.update_layout(
                title=dict(
                    text='차원별 분포 분석',
                    font=dict(size=18, color='#2C3E50'),
                    x=0.5,
                    xanchor='center'
                ),
                height=400,
                width=1200,
                showlegend=False,
                margin=dict(l=50, r=50, t=80, b=80)
            )

            # Update axes
            for i in range(1, 4):
                fig.update_yaxes(title_text="비율 (%)", range=[0, max(stage_values + context_values + level_values) * 1.2], row=1, col=i)

            html = self._generate_html_wrapper(fig)

            logger.info("Distribution charts generated successfully")
            return html

        except Exception as e:
            logger.error(f"Distribution chart generation failed: {str(e)}")
            return self._generate_error_visualization(str(e))

    def _prepare_3d_data(self, matrix: Dict[str, Any]) -> tuple:
        """Prepare data for 3D visualization"""
        x_coords = []
        y_coords = []
        z_coords = []
        values = []
        hover_texts = []

        # Iterate through all combinations
        for stage_idx, stage_name in enumerate(['introduction', 'development', 'closing']):
            stage_data = matrix.get(stage_name, {})

            for context_idx, context_name in enumerate(['explanation', 'question', 'feedback', 'facilitation', 'management']):
                context_data = stage_data.get(context_name, {})

                for level_idx, level_name in enumerate(['l1', 'l2', 'l3']):
                    count = context_data.get(level_name, 0)

                    if count > 0:  # Only include non-zero values
                        x_coords.append(stage_idx)
                        y_coords.append(context_idx)
                        z_coords.append(level_idx)
                        values.append(count)

                        hover_text = f"{self.stage_labels[stage_idx]} - {self.context_labels[context_idx]} - {self.level_labels[level_idx]}"
                        hover_texts.append(hover_text)

        return x_coords, y_coords, z_coords, values, hover_texts

    def _prepare_2d_slice(self, matrix: Dict[str, Any], level_idx: int) -> tuple:
        """Prepare data for 2D heatmap slice"""
        level_map = {0: 'l1', 1: 'l2', 2: 'l3'}
        level_key = level_map[level_idx]

        # Initialize matrix
        z_data = np.zeros((len(self.context_labels), len(self.stage_labels)))

        # Fill matrix
        for stage_idx, stage_name in enumerate(['introduction', 'development', 'closing']):
            stage_data = matrix.get(stage_name, {})

            for context_idx, context_name in enumerate(['explanation', 'question', 'feedback', 'facilitation', 'management']):
                context_data = stage_data.get(context_name, {})
                count = context_data.get(level_key, 0)
                z_data[context_idx][stage_idx] = count

        return z_data, self.stage_labels, self.context_labels

    def _generate_html_wrapper(self, fig: go.Figure) -> str:
        """Wrap Plotly figure in HTML"""
        # Convert to HTML
        html = fig.to_html(
            include_plotlyjs='cdn',
            div_id='plotly-chart',
            config={
                'responsive': True,
                'displayModeBar': True,
                'displaylogo': False,
                'modeBarButtonsToRemove': ['lasso2d', 'select2d']
            }
        )

        # Add custom styling
        html = f'''
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>3D Matrix Visualization</title>
    <style>
        body {{
            font-family: 'Nanum Gothic', 'Apple SD Gothic Neo', sans-serif;
            margin: 0;
            padding: 20px;
            background: #f8f9fa;
        }}
        #plotly-chart {{
            background: white;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            padding: 20px;
        }}
    </style>
</head>
<body>
    {html}
</body>
</html>
'''
        return html

    def _generate_empty_visualization(self) -> str:
        """Generate empty placeholder visualization"""
        return '''
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <title>Visualization</title>
    <style>
        body {
            font-family: 'Nanum Gothic', sans-serif;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            margin: 0;
            background: #f8f9fa;
        }
        .message {
            text-align: center;
            color: #666;
        }
    </style>
</head>
<body>
    <div class="message">
        <h2>시각화 데이터 없음</h2>
        <p>매트릭스 데이터가 제공되지 않았습니다.</p>
    </div>
</body>
</html>
'''

    def _generate_error_visualization(self, error_msg: str) -> str:
        """Generate error visualization"""
        return f'''
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <title>Visualization Error</title>
    <style>
        body {{
            font-family: 'Nanum Gothic', sans-serif;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            margin: 0;
            background: #f8f9fa;
        }}
        .error {{
            text-align: center;
            color: #d32f2f;
            padding: 30px;
            background: white;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }}
    </style>
</head>
<body>
    <div class="error">
        <h2>시각화 생성 오류</h2>
        <p>{error_msg}</p>
    </div>
</body>
</html>
'''


# ============ Demo/Test Code ============

if __name__ == "__main__":
    print("=" * 60)
    print("3D Matrix Visualizer Demo")
    print("=" * 60)
    print("\nThis module generates interactive 3D visualizations.")
    print("Usage: Import and use in main.py endpoints")
    print("\nFeatures:")
    print("  ✓ Interactive 3D heatmap (Plotly)")
    print("  ✓ 2D heatmap slices by cognitive level")
    print("  ✓ Distribution bar charts")
    print("  ✓ Responsive HTML output")
    print("\n" + "=" * 60)
