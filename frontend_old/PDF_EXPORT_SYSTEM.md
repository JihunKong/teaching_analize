# AIBOA PDF Export System

A comprehensive PDF export system for the AIBOA (AI-Based Observation and Analysis) platform that provides high-quality PDF generation with extensive customization options, batch processing capabilities, and professional formatting.

## 🚀 Features

### Core PDF Export Capabilities
- **Multiple PDF Formats**: A4, Letter, A3, Legal, and custom sizes
- **High-Quality Output**: Configurable DPI settings (72-300) and quality levels
- **Korean Font Support**: Optimized for Korean text with proper font rendering
- **Chart Integration**: Seamless rendering of charts and graphs in PDF format
- **Professional Layout**: Headers, footers, page numbers, and table of contents

### Advanced Features
- **Batch Export**: Generate multiple PDFs simultaneously with queue management
- **Real-time Preview**: Live PDF preview before generation
- **Progress Tracking**: Detailed progress indicators with time estimation
- **Error Recovery**: Automatic retry mechanisms with customizable settings
- **Export History**: Track and manage previously generated PDFs
- **Watermarking**: Custom watermarks with adjustable opacity

### Report Types
1. **Comprehensive Reports**: Complete analysis with all frameworks
2. **Summary Reports**: Condensed key insights and recommendations
3. **Action Plans**: Detailed improvement strategies with timelines
4. **Individual Framework Reports**: Focused analysis per framework
5. **Comparison Reports**: Side-by-side analysis comparisons
6. **Portfolio Reports**: Collection of reports over time

## 📁 System Architecture

```
src/
├── lib/
│   └── pdf-export.ts              # Core PDF export service
├── hooks/
│   └── usePDFExport.ts            # PDF export hook with state management
├── components/
│   ├── pdf/
│   │   ├── PDFExportButton.tsx    # Main export button component
│   │   ├── PDFOptions.tsx         # Comprehensive options panel
│   │   ├── PDFPreview.tsx         # PDF preview component
│   │   ├── BatchPDFExport.tsx     # Batch export management
│   │   └── index.ts               # Component exports
│   ├── settings/
│   │   └── PDFSettings.tsx        # Global PDF settings
│   └── reports/                   # Enhanced with PDF export
│       ├── ComprehensiveReportTemplate.tsx
│       ├── SummaryReportTemplate.tsx
│       └── ActionPlanTemplate.tsx
└── app/
    └── pdf-demo/
        └── page.tsx               # Complete demo page
```

## 🛠 Installation

### Dependencies
```bash
npm install html2pdf.js jspdf html2canvas canvas
npm install @radix-ui/react-checkbox @radix-ui/react-slider @radix-ui/react-tabs @radix-ui/react-select
```

### Core Dependencies
- **html2pdf.js**: Primary PDF generation engine
- **jsPDF**: Advanced PDF manipulation
- **html2canvas**: HTML to canvas conversion for high-quality rendering
- **canvas**: Server-side canvas rendering support

## 🎯 Usage

### Basic PDF Export

```tsx
import { PDFExportButton } from '@/components/pdf'

function MyComponent() {
  return (
    <PDFExportButton
      html={reportHTML}
      filename="my-report.pdf"
      title="Export Report"
      showOptionsDialog={true}
      showProgress={true}
      onExportComplete={(success, result) => {
        if (success) {
          console.log('Export successful:', result)
        }
      }}
    />
  )
}
```

### Advanced Options

```tsx
import { PDFExportButton, pdfExportUtils } from '@/components/pdf'

function AdvancedExport() {
  const customOptions = {
    format: 'A4',
    orientation: 'portrait',
    quality: 'high',
    dpi: 300,
    includePageNumbers: true,
    includeWatermark: true,
    watermarkText: 'CONFIDENTIAL',
    koreanFont: true,
    margin: { top: 20, bottom: 20, left: 15, right: 15 }
  }

  return (
    <PDFExportButton
      html={reportHTML}
      filename="advanced-report.pdf"
      defaultOptions={customOptions}
      showOptionsDialog={true}
    />
  )
}
```

### Batch Export

```tsx
import { BatchPDFExport } from '@/components/pdf'

function BatchExportDemo() {
  const batchItems = [
    {
      id: 'report1',
      title: 'Comprehensive Analysis',
      html: report1HTML
    },
    {
      id: 'report2',
      title: 'Summary Report',
      html: report2HTML
    }
  ]

  return (
    <BatchPDFExport
      items={batchItems}
      showCombinedOption={true}
      onExportComplete={(results) => {
        console.log('Batch export completed:', results)
      }}
    />
  )
}
```

### PDF Preview

```tsx
import { PDFPreview } from '@/components/pdf'

function PreviewDemo() {
  return (
    <PDFPreview
      html={reportHTML}
      options={{ format: 'A4', quality: 'high' }}
      filename="preview.pdf"
      showControls={true}
      showInfo={true}
      autoGenerate={true}
    />
  )
}
```

### Using the Hook

```tsx
import { usePDFExport } from '@/hooks/usePDFExport'

function CustomExportComponent() {
  const {
    exportToPDF,
    batchExportToPDF,
    createPreview,
    isExporting,
    currentProgress,
    exportState
  } = usePDFExport()

  const handleExport = async () => {
    try {
      const result = await exportToPDF(
        reportHTML,
        'custom-report.pdf',
        { quality: 'high', format: 'A4' }
      )
      console.log('Export result:', result)
    } catch (error) {
      console.error('Export failed:', error)
    }
  }

  return (
    <div>
      <button onClick={handleExport} disabled={isExporting}>
        {isExporting ? 'Exporting...' : 'Export PDF'}
      </button>
      {currentProgress && (
        <div>Progress: {currentProgress.progress}%</div>
      )}
    </div>
  )
}
```

## ⚙️ Configuration Options

### PDF Export Options

```typescript
interface PDFExportOptions {
  // Format settings
  format: 'A4' | 'Letter' | 'A3' | 'Legal' | 'Custom'
  orientation: 'portrait' | 'landscape'
  customSize?: { width: number; height: number }
  
  // Quality settings
  quality: 'low' | 'medium' | 'high' | 'ultra'
  dpi: 72 | 96 | 150 | 300
  
  // Layout settings
  margin: {
    top: number
    bottom: number
    left: number
    right: number
  }
  
  // Content settings
  includePageNumbers: boolean
  includeHeader: boolean
  includeFooter: boolean
  includeWatermark: boolean
  includeCharts: boolean
  
  // Metadata
  title?: string
  author?: string
  subject?: string
  keywords?: string[]
  
  // Korean font support
  koreanFont: boolean
  fontFamily?: string
  
  // Branding
  watermarkText?: string
  watermarkOpacity?: number
  
  // Advanced settings
  enableOptimization: boolean
  compressImages: boolean
  breakPages: boolean
  tableOfContents: boolean
}
```

### Default Settings

```typescript
export const DEFAULT_PDF_OPTIONS: PDFExportOptions = {
  format: 'A4',
  orientation: 'portrait',
  quality: 'high',
  dpi: 150,
  margin: { top: 20, bottom: 20, left: 15, right: 15 },
  includePageNumbers: true,
  includeHeader: true,
  includeFooter: true,
  includeWatermark: false,
  includeCharts: true,
  koreanFont: true,
  fontFamily: 'NanumGothic, Arial, sans-serif',
  enableOptimization: true,
  compressImages: true,
  breakPages: true,
  tableOfContents: false
}
```

## 🎨 Report Template Integration

All report templates now include integrated PDF export functionality:

### Enhanced Templates

```tsx
// Comprehensive Report with PDF Export
<ComprehensiveReportTemplate
  analysisResult={data}
  metadata={metadata}
  showPDFExport={true}
  enablePreview={true}
/>

// Summary Report with PDF Export
<SummaryReportTemplate
  analysisResult={data}
  metadata={metadata}
  showPDFExport={true}
  enablePreview={true}
/>

// Action Plan with PDF Export
<ActionPlanTemplate
  analysisResult={data}
  metadata={metadata}
  showPDFExport={true}
  enablePreview={true}
/>
```

## 📊 Performance Optimization

### Optimization Features
- **Image Compression**: Automatic image optimization for smaller file sizes
- **Content Optimization**: Removal of interactive elements and optimization for print
- **Memory Management**: Efficient cleanup of temporary resources
- **Batch Processing**: Queue-based processing for multiple exports
- **Caching**: Intelligent caching of preview generations

### Performance Tips
- Use `quality: 'medium'` for faster generation during development
- Enable `compressImages: true` for smaller file sizes
- Use `dpi: 150` for balanced quality and performance
- Consider `enableOptimization: true` for production exports

## 🔧 Settings Management

### Global Settings

```tsx
import { PDFSettings } from '@/components/settings/PDFSettings'

function SettingsPage() {
  return (
    <PDFSettings
      onSettingsChange={(settings) => {
        console.log('Settings updated:', settings)
      }}
    />
  )
}
```

### Settings Categories
- **Default Options**: Format, quality, and layout defaults
- **Behavior Settings**: Auto-download, preview, and progress options
- **History Management**: Export history and cleanup settings
- **Performance Settings**: Optimization and resource management

## 📝 Export History

The system automatically tracks all PDF exports with:
- **Export Metadata**: Title, file size, page count, generation time
- **Download Management**: Re-download previously generated PDFs
- **Storage Optimization**: Configurable history retention
- **Search and Filter**: Find specific exports quickly

## 🚨 Error Handling

### Automatic Recovery
- **Retry Logic**: Configurable retry attempts for failed exports
- **Error Reporting**: Detailed error messages with suggestions
- **Graceful Degradation**: Fallback options for unsupported features
- **Progress Recovery**: Resume interrupted batch operations

### Common Issues and Solutions

#### Korean Font Issues
```typescript
// Ensure Korean font support is enabled
const options = {
  koreanFont: true,
  fontFamily: 'NanumGothic, Arial, sans-serif'
}
```

#### Large File Performance
```typescript
// Optimize for large files
const options = {
  quality: 'medium',
  dpi: 96,
  compressImages: true,
  enableOptimization: true
}
```

#### Chart Rendering Issues
```typescript
// Ensure charts are properly included
const options = {
  includeCharts: true,
  quality: 'high' // Higher quality for better chart rendering
}
```

## 🧪 Testing

### Demo Page
Visit `/pdf-demo` to test all PDF export features:
- Individual report exports
- Batch export functionality
- PDF preview capabilities
- Settings management
- Template integration

### Test Scenarios
1. **Basic Export**: Single report with default settings
2. **Custom Options**: Modified format, quality, and layout
3. **Batch Processing**: Multiple reports with different settings
4. **Preview Testing**: Real-time preview generation
5. **Error Handling**: Network issues and invalid content

## 🔮 Future Enhancements

### Planned Features
- **Cloud Storage Integration**: Direct upload to cloud services
- **Email Integration**: Send PDFs directly via email
- **Digital Signatures**: Add digital signatures to PDFs
- **Template Designer**: Visual PDF template editor
- **API Integration**: RESTful API for server-side generation
- **Mobile Optimization**: Enhanced mobile PDF generation

### Advanced Integrations
- **Print Server**: Dedicated server for high-volume PDF generation
- **Document Management**: Integration with document management systems
- **Workflow Automation**: Automated PDF generation triggers
- **Analytics**: Detailed export analytics and usage patterns

## 📞 Support

For technical support or feature requests related to the PDF export system:

1. Check the demo page for examples: `/pdf-demo`
2. Review the component documentation in each file
3. Test with sample data before production use
4. Monitor export history for troubleshooting

## 📄 License

This PDF export system is part of the AIBOA platform and follows the same licensing terms.

---

**Note**: This PDF export system is designed specifically for the AIBOA platform and includes Korean language optimizations and educational report formatting. It provides a complete solution for generating professional-quality PDF reports from web-based analysis results.