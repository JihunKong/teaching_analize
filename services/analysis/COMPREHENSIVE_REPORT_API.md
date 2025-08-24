# Comprehensive Report Generation API

## Overview

The AIBOA Analysis Service now supports comprehensive report generation that combines multiple analysis frameworks into unified reports with multi-framework comparison, normalized scoring, and integrated insights.

## New API Endpoints

### 1. Generate Comprehensive Report

**Endpoint:** `POST /api/reports/generate/comprehensive`

**Description:** Generate comprehensive HTML report combining multiple analysis results

**Request Body:**
```json
{
  "job_ids": ["uuid1", "uuid2", "uuid3"],
  "report_type": "comparison",
  "framework_weights": {
    "cbil": 1.0,
    "student_discussion": 1.2,
    "lesson_coaching": 0.8
  },
  "include_recommendations": true,
  "title": "종합 교육 분석 보고서"
}
```

**Request Parameters:**
- `job_ids` (required): Array of analysis job IDs to combine (1-10 jobs)
- `report_type` (optional): Report type - "comparison", "detailed", or "executive" (default: "comparison")
- `framework_weights` (optional): Dictionary of framework weights for scoring (default: equal weights)
- `include_recommendations` (optional): Whether to include recommendations section (default: true)
- `title` (optional): Custom report title (default: "종합 교육 분석 보고서")

**Response:**
- **Content-Type:** `text/html; charset=utf-8`
- **Body:** Complete HTML report with:
  - Executive summary with overall score
  - Framework comparison charts
  - Individual framework analysis cards
  - Unified insights and strengths/improvements
  - Integrated recommendations
  - Interactive Chart.js visualizations

**Response Headers:**
- `X-Analysis-Count`: Number of analyses successfully combined
- `X-Missing-Jobs`: Number of requested jobs that were not found
- `X-Failed-Jobs`: Number of jobs that failed or weren't completed

**Error Responses:**
```json
// 400 Bad Request - No valid results
{
  "detail": {
    "message": "No valid analysis results found for comprehensive report",
    "missing_jobs": ["job1", "job2"],
    "failed_jobs": [
      {"job_id": "job3", "status": "failed", "message": "Analysis failed"}
    ],
    "total_requested": 3
  }
}

// 422 Validation Error
{
  "detail": [
    {
      "loc": ["body", "job_ids"],
      "msg": "At least one job_id is required",
      "type": "value_error"
    }
  ]
}
```

### 2. Check Comprehensive Report Status

**Endpoint:** `GET /api/reports/comprehensive/status/{job_ids}`

**Description:** Check status of multiple analysis jobs for comprehensive reporting

**Path Parameters:**
- `job_ids`: Comma-separated list of job IDs (e.g., "job1,job2,job3")

**Response:**
```json
{
  "job_statuses": [
    {
      "job_id": "uuid1",
      "status": "completed",
      "framework": "cbil",
      "framework_name": "개념기반 탐구 수업(CBIL) 분석",
      "message": "Analysis completed successfully",
      "has_result": true,
      "created_at": "2024-01-15T10:00:00",
      "updated_at": "2024-01-15T10:05:00"
    }
  ],
  "summary": {
    "total_jobs": 3,
    "completed": 2,
    "processing": 1,
    "pending": 0,
    "failed": 0,
    "missing": 0,
    "ready_for_comprehensive": false
  },
  "timestamp": "2024-01-15T10:30:00"
}
```

## Features

### Score Normalization

All framework scores are normalized to a 0-100 scale for fair comparison:

- **CBIL:** 0-3 discrete scale → 0-100 scale
- **Student Discussion:** 0-10+ frequency scale → 0-100 scale  
- **Lesson Coaching:** Already percentage-based → 0-100 scale

### Framework Weighting

Custom weights can be applied to frameworks:

```json
{
  "framework_weights": {
    "cbil": 1.0,           // Standard weight
    "student_discussion": 1.2,  // 20% more important
    "lesson_coaching": 0.8      // 20% less important
  }
}
```

### Report Sections

1. **Executive Summary**
   - Overall teaching effectiveness score
   - Key statistics and metrics
   - Analysis overview

2. **Framework Comparison**
   - Side-by-side framework cards
   - Interactive comparison charts
   - Normalized scoring display

3. **Unified Insights**
   - Combined strengths across all frameworks
   - Common improvement areas
   - Cross-framework patterns

4. **Integrated Recommendations**
   - Prioritized action items
   - Combined suggestions from all analyses
   - Actionable improvement steps

### Error Handling

The API handles various error scenarios gracefully:

- **Missing Jobs:** Jobs not found in Redis are reported but don't fail the request
- **Failed Jobs:** Jobs with non-completed status are listed in error details
- **Partial Success:** Reports are generated even if some jobs fail
- **Data Validation:** Invalid weights and job ID limits are enforced
- **Malformed Data:** Graceful handling of corrupted analysis results

## Usage Examples

### Basic Comprehensive Report

```bash
curl -X POST "http://localhost:8001/api/reports/generate/comprehensive" \
  -H "Content-Type: application/json" \
  -d '{
    "job_ids": ["analysis-1", "analysis-2"],
    "report_type": "comparison"
  }'
```

### Advanced Report with Custom Configuration

```bash
curl -X POST "http://localhost:8001/api/reports/generate/comprehensive" \
  -H "Content-Type: application/json" \
  -d '{
    "job_ids": ["cbil-analysis", "discussion-analysis", "coaching-analysis"],
    "report_type": "comparison",
    "framework_weights": {
      "cbil": 1.0,
      "student_discussion": 1.3,
      "lesson_coaching": 0.7
    },
    "include_recommendations": true,
    "title": "Multi-Framework Teaching Effectiveness Report"
  }'
```

### Check Report Readiness

```bash
curl "http://localhost:8001/api/reports/comprehensive/status/job1,job2,job3"
```

## Integration Notes

### Frontend Integration

```javascript
// Check if analyses are ready for comprehensive report
const checkStatus = async (jobIds) => {
  const response = await fetch(
    `/api/reports/comprehensive/status/${jobIds.join(',')}`
  );
  const status = await response.json();
  return status.summary.ready_for_comprehensive;
};

// Generate comprehensive report
const generateReport = async (jobIds, config = {}) => {
  const response = await fetch('/api/reports/generate/comprehensive', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      job_ids: jobIds,
      ...config
    })
  });
  
  if (response.ok) {
    return await response.text(); // HTML content
  } else {
    throw new Error(await response.json());
  }
};
```

### Database Integration

The comprehensive report system integrates with the existing database structure:

- Analysis results are retrieved from Redis cache
- Framework usage statistics are updated
- Report generation is logged for research purposes
- No additional database schema changes required

## Performance Considerations

- **Memory Usage:** Reports are generated in-memory; suitable for up to 10 analyses
- **Processing Time:** Typically 1-3 seconds for 2-5 framework combination
- **Caching:** Individual analysis results are cached; comprehensive reports are generated on-demand
- **Scalability:** Redis-based job storage supports high concurrency

## Security

- **Input Validation:** Job IDs and weights are validated before processing
- **Rate Limiting:** Maximum 10 analyses per comprehensive report
- **Error Information:** Detailed error responses help with debugging
- **Data Privacy:** No sensitive information is logged in error messages

## Future Enhancements

1. **PDF Export:** Extend PDF generator to support comprehensive reports
2. **Template Customization:** Additional report templates and layouts
3. **Batch Processing:** Support for generating multiple comprehensive reports
4. **Analytics Dashboard:** Track comprehensive report usage patterns
5. **Export Formats:** JSON, CSV exports of aggregated analysis data