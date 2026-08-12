import React, { useState } from 'react';
import axios from 'axios';
import {
  FileText,
  UploadCloud,
  Link as LinkIcon,
  Code,
  Tag,
  AlertCircle,
  Copy,
  Check,
  Sparkles,
  Cpu,
  ArrowRight,
  CheckCircle2,
  FileSpreadsheet,
  Box,
  RefreshCw
} from 'lucide-react';

const API_BASE_URL = 'http://localhost:8000/api/product-input';

export default function App() {
  const [activeTab, setActiveTab] = useState('PDF'); // PDF, CSV, URL, JSON, PRODUCT_NAME
  const [file, setFile] = useState(null);
  const [productName, setProductName] = useState('');
  const [url, setUrl] = useState('');
  const [jsonText, setJsonText] = useState('');

  const [loading, setLoading] = useState(false);
  const [response, setResponse] = useState(null);
  const [error, setError] = useState(null);
  const [copied, setCopied] = useState(false);

  // Tab switching helper - resets file and errors to avoid cross-tab file confusion
  const handleTabChange = (tabId) => {
    setActiveTab(tabId);
    setError(null);
    setFile(null);
  };

  // Load preset demo samples for easy 1-click testing across all tabs
  const loadPreset = (type) => {
    setError(null);
    if (type === 'PDF') {
      setActiveTab('PDF');
      // Create sample PDF file blob with valid PDF structure & text content
      const samplePdfBytes = new Uint8Array([
        0x25, 0x50, 0x44, 0x46, 0x2d, 0x31, 0x2e, 0x34, 0x0a, 0x31, 0x20, 0x30, 0x20, 0x6f, 0x62, 0x6a,
        0x0a, 0x3c, 0x3c, 0x2f, 0x54, 0x79, 0x70, 0x65, 0x2f, 0x43, 0x61, 0x74, 0x61, 0x6c, 0x6f, 0x67,
        0x2f, 0x50, 0x61, 0x67, 0x65, 0x73, 0x20, 0x32, 0x20, 0x30, 0x20, 0x52, 0x3e, 0x3e, 0x0a, 0x65,
        0x6e, 0x64, 0x6f, 0x62, 0x6a, 0x0a, 0x32, 0x20, 0x30, 0x20, 0x6f, 0x62, 0x6a, 0x0a, 0x3c, 0x3c,
        0x2f, 0x54, 0x79, 0x70, 0x65, 0x2f, 0x50, 0x61, 0x67, 0x65, 0x73, 0x2f, 0x4b, 0x69, 0x64, 0x73,
        0x5b, 0x33, 0x20, 0x30, 0x20, 0x52, 0x5d, 0x2f, 0x43, 0x6f, 0x75, 0x6e, 0x74, 0x20, 0x31, 0x3e,
        0x3e, 0x0a, 0x65, 0x6e, 0x64, 0x6f, 0x62, 0x6a, 0x0a, 0x33, 0x20, 0x30, 0x20, 0x6f, 0x62, 0x6a,
        0x0a, 0x3c, 0x3c, 0x2f, 0x54, 0x79, 0x70, 0x65, 0x2f, 0x50, 0x61, 0x67, 0x65, 0x2f, 0x50, 0x61,
        0x72, 0x65, 0x6e, 0x74, 0x20, 0x32, 0x20, 0x30, 0x20, 0x52, 0x2f, 0x4d, 0x65, 0x64, 0x69, 0x61,
        0x42, 0x6f, 0x78, 0x5b, 0x30, 0x20, 0x30, 0x20, 0x36, 0x31, 0x32, 0x20, 0x37, 0x39, 0x32, 0x5d,
        0x2f, 0x43, 0x6f, 0x6e, 0x74, 0x65, 0x6e, 0x74, 0x73, 0x20, 0x34, 0x20, 0x30, 0x20, 0x52, 0x2f,
        0x52, 0x65, 0x73, 0x6f, 0x75, 0x72, 0x63, 0x65, 0x73, 0x3c, 0x3c, 0x2f, 0x46, 0x6f, 0x6e, 0x74,
        0x3c, 0x3c, 0x2f, 0x46, 0x31, 0x20, 0x35, 0x20, 0x30, 0x20, 0x52, 0x3e, 0x3e, 0x3e, 0x3e, 0x0a,
        0x65, 0x6e, 0x64, 0x6f, 0x62, 0x6a, 0x0a, 0x34, 0x20, 0x30, 0x20, 0x6f, 0x62, 0x6a, 0x0a, 0x3c,
        0x3c, 0x2f, 0x4c, 0x65, 0x6e, 0x67, 0x74, 0x68, 0x20, 0x31, 0x31, 0x30, 0x3e, 0x3e, 0x0a, 0x73,
        0x74, 0x72, 0x65, 0x61, 0x6d, 0x0a, 0x42, 0x54, 0x0a, 0x2f, 0x46, 0x31, 0x20, 0x31, 0x32, 0x20,
        0x54, 0x66, 0x0a, 0x37, 0x30, 0x20, 0x37, 0x30, 0x30, 0x20, 0x54, 0x64, 0x0a, 0x28, 0x41, 0x42,
        0x42, 0x20, 0x41, 0x43, 0x53, 0x38, 0x38, 0x30, 0x20, 0x49, 0x6e, 0x64, 0x75, 0x73, 0x74, 0x72,
        0x69, 0x61, 0x6c, 0x20, 0x44, 0x72, 0x69, 0x76, 0x65, 0x20, 0x44, 0x61, 0x74, 0x61, 0x73, 0x68,
        0x65, 0x65, 0x74, 0x20, 0x4d, 0x61, 0x6e, 0x75, 0x66, 0x61, 0x63, 0x74, 0x75, 0x72, 0x65, 0x72,
        0x3a, 0x20, 0x41, 0x42, 0x42, 0x20, 0x4d, 0x6f, 0x64, 0x65, 0x6c, 0x3a, 0x20, 0x41, 0x43, 0x53,
        0x38, 0x38, 0x30, 0x2d, 0x30, 0x31, 0x20, 0x53, 0x4b, 0x55, 0x3a, 0x20, 0x33, 0x41, 0x55, 0x41,
        0x30, 0x30, 0x30, 0x30, 0x31, 0x32, 0x33, 0x34, 0x35, 0x29, 0x20, 0x54, 0x6a, 0x0a, 0x45, 0x54,
        0x0a, 0x65, 0x6e, 0x64, 0x73, 0x74, 0x72, 0x65, 0x61, 0x6d, 0x0a, 0x65, 0x6e, 0x64, 0x6f, 0x62,
        0x6a, 0x0a, 0x35, 0x20, 0x30, 0x20, 0x6f, 0x62, 0x6a, 0x0a, 0x3c, 0x3c, 0x2f, 0x54, 0x79, 0x70,
        0x65, 0x2f, 0x46, 0x6f, 0x6e, 0x74, 0x2f, 0x53, 0x75, 0x62, 0x74, 0x79, 0x70, 0x65, 0x2f, 0x54,
        0x79, 0x70, 0x65, 0x31, 0x2f, 0x42, 0x61, 0x73, 0x65, 0x46, 0x6f, 0x6e, 0x74, 0x2f, 0x48, 0x65,
        0x6c, 0x76, 0x65, 0x74, 0x69, 0x63, 0x61, 0x3e, 0x3e, 0x0a, 0x65, 0x6e, 0x64, 0x6f, 0x62, 0x6a,
        0x0a, 0x78, 0x72, 0x65, 0x66, 0x0a, 0x30, 0x20, 0x36, 0x0a, 0x30, 0x30, 0x30, 0x30, 0x30, 0x30,
        0x30, 0x30, 0x30, 0x30, 0x20, 0x36, 0x35, 0x35, 0x33, 0x35, 0x20, 0x66, 0x20, 0x0a, 0x30, 0x30,
        0x30, 0x30, 0x30, 0x30, 0x30, 0x30, 0x30, 0x39, 0x20, 0x30, 0x30, 0x30, 0x30, 0x30, 0x20, 0x6e,
        0x20, 0x0a, 0x30, 0x30, 0x30, 0x30, 0x30, 0x30, 0x30, 0x30, 0x35, 0x38, 0x20, 0x30, 0x30, 0x30,
        0x30, 0x30, 0x20, 0x6e, 0x20, 0x0a, 0x30, 0x30, 0x30, 0x30, 0x30, 0x30, 0x30, 0x31, 0x31, 0x35,
        0x20, 0x30, 0x30, 0x30, 0x30, 0x30, 0x20, 0x6e, 0x20, 0x0a, 0x30, 0x30, 0x30, 0x30, 0x30, 0x30,
        0x30, 0x32, 0x36, 0x31, 0x20, 0x30, 0x30, 0x30, 0x30, 0x30, 0x20, 0x6e, 0x20, 0x0a, 0x30, 0x30,
        0x30, 0x30, 0x30, 0x30, 0x30, 0x34, 0x32, 0x31, 0x20, 0x30, 0x30, 0x30, 0x30, 0x30, 0x20, 0x6e,
        0x20, 0x0a, 0x74, 0x72, 0x61, 0x69, 0x6c, 0x65, 0x72, 0x0a, 0x3c, 0x3c, 0x2f, 0x53, 0x69, 0x7a,
        0x65, 0x20, 0x36, 0x2f, 0x52, 0x6f, 0x6f, 0x74, 0x20, 0x31, 0x20, 0x30, 0x20, 0x52, 0x3e, 0x3e,
        0x0a, 0x73, 0x74, 0x61, 0x72, 0x74, 0x78, 0x72, 0x65, 0x66, 0x0a, 0x34, 0x39, 0x34, 0x0a, 0x25,
        0x25, 0x45, 0x4f, 0x46, 0x0a
      ]);
      const pdfBlob = new Blob([samplePdfBytes], { type: 'application/pdf' });
      const pdfSampleFile = new File([pdfBlob], 'sample_abb_datasheet.pdf', { type: 'application/pdf' });
      setFile(pdfSampleFile);

    } else if (type === 'CSV') {
      setActiveTab('CSV');
      // Create sample CSV file blob
      const csvContent = `SKU,Product Name,Brand,Manufacturer,Model,Category\nACS880-01-145A-3,ABB ACS880 Industrial Drive,ABB,ABB,ACS880,Industrial Drives\nATV320U15N4B,Schneider Altivar 320,Schneider Electric,Schneider Electric,ATV320,Variable Speed Drives`;
      const csvBlob = new Blob([csvContent], { type: 'text/csv' });
      const csvSampleFile = new File([csvBlob], 'sample_products_catalog.csv', { type: 'text/csv' });
      setFile(csvSampleFile);

    } else if (type === 'PRODUCT_NAME') {
      setActiveTab('PRODUCT_NAME');
      setProductName('ABB ACS880 Industrial Drive\nManufacturer: ABB\nModel: ACS880-01-145A-3\nSKU: 3AUA000012345');
    } else if (type === 'URL') {
      setActiveTab('URL');
      setUrl('https://example.com');
    } else if (type === 'JSON') {
      setActiveTab('JSON');
      setJsonText(JSON.stringify({
        product_name: "SKF 6205 Deep Groove Ball Bearing",
        brand: "SKF",
        manufacturer: "SKF Group",
        model: "6205-2RSH",
        sku: "6205",
        part_number: "6205-2RSH/C3",
        dimensions: "25x52x15 mm",
        category: "Bearings"
      }, null, 2));
    }
  };

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setResponse(null);

    try {
      let res;
      if (activeTab === 'PDF' || activeTab === 'CSV') {
        const expectedExt = activeTab.toLowerCase();
        if (!file || !file.name.toLowerCase().endsWith('.' + expectedExt)) {
          throw new Error(`Please select or upload a valid .${expectedExt} file.`);
        }
        const formData = new FormData();
        formData.append('file', file);
        formData.append('input_type', activeTab);
        res = await axios.post(API_BASE_URL, formData, {
          headers: { 'Content-Type': 'multipart/form-data' }
        });
      } else if (activeTab === 'PRODUCT_NAME') {
        if (!productName.trim()) {
          throw new Error('Please enter a product name or text details.');
        }
        const formData = new FormData();
        formData.append('input_text', productName);
        formData.append('input_type', 'PRODUCT_NAME');
        res = await axios.post(API_BASE_URL, formData);
      } else if (activeTab === 'URL') {
        if (!url.trim()) {
          throw new Error('Please enter a target URL.');
        }
        const formData = new FormData();
        formData.append('url', url);
        formData.append('input_type', 'URL');
        res = await axios.post(API_BASE_URL, formData);
      } else if (activeTab === 'JSON') {
        if (!jsonText.trim()) {
          throw new Error('Please enter JSON payload text.');
        }
        let parsed;
        try {
          parsed = JSON.parse(jsonText);
        } catch (err) {
          throw new Error('Invalid JSON string syntax. Please verify JSON structure.');
        }
        res = await axios.post(API_BASE_URL, {
          input_type: 'JSON',
          json_data: parsed
        });
      }

      if (res && res.data) {
        if (res.data.status === 'ERROR') {
          setError(res.data.error || 'Processing error occurred.');
        } else {
          setResponse(res.data);
        }
      }
    } catch (err) {
      if (err.response && err.response.data && err.response.data.error) {
        setError(err.response.data.error);
      } else {
        setError(err.message || 'Failed to connect to backend server. Make sure FastAPI backend is running on http://localhost:8000.');
      }
    } finally {
      setLoading(false);
    }
  };

  const copyJsonToClipboard = () => {
    if (response) {
      navigator.clipboard.writeText(JSON.stringify(response, null, 2));
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col font-sans selection:bg-indigo-500 selection:text-white">
      {/* Header Bar */}
      <header className="border-b border-slate-800 bg-slate-900/80 backdrop-blur-md sticky top-0 z-50 px-6 py-4">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-indigo-600 to-violet-500 flex items-center justify-center shadow-lg shadow-indigo-500/20">
              <Cpu className="w-6 h-6 text-white" />
            </div>
            <div>
              <h1 className="text-xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-white via-slate-200 to-indigo-300">
                ProductDNA
              </h1>
              <p className="text-xs text-slate-400 font-medium">
                Module 1 — Product Intake & Document Processing
              </p>
            </div>
          </div>

          <div className="flex items-center space-x-3">
            <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
              <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse mr-2"></span>
              API Ready (v1.0)
            </span>
          </div>
        </div>
      </header>

      {/* Main Container */}
      <main className="flex-1 max-w-7xl w-full mx-auto p-6 space-y-8">
        
        {/* Intro Hero Section */}
        <section className="bg-gradient-to-r from-slate-900 via-indigo-950/40 to-slate-900 rounded-2xl p-6 border border-slate-800 shadow-xl relative overflow-hidden">
          <div className="absolute top-0 right-0 w-96 h-96 bg-indigo-500/10 rounded-full blur-3xl -mr-20 -mt-20 pointer-events-none"></div>
          <div className="relative z-10 space-y-2">
            <h2 className="text-2xl font-bold text-white tracking-tight">
              Product Intake Studio
            </h2>
            <p className="text-sm text-slate-300 max-w-3xl leading-relaxed">
              Convert raw, unstructured product inputs (PDF datasheets, CSV catalogs, Web URLs, JSON payloads, or text strings) into standardized 
              <code className="mx-1.5 px-2 py-0.5 rounded bg-slate-800 text-indigo-300 text-xs font-mono border border-slate-700">StandardProductInput</code> objects for Module 2 Resolution.
            </p>
          </div>
        </section>

        {/* Input Configuration Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
          
          {/* Left Panel: Input Controls */}
          <div className="lg:col-span-6 space-y-6">
            <div className="bg-slate-900/90 rounded-2xl border border-slate-800 p-6 shadow-xl space-y-6">
              
              {/* Type Selector Tabs */}
              <div>
                <label className="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-3">
                  1. Select Input Type
                </label>
                <div className="grid grid-cols-5 gap-2 bg-slate-950 p-1.5 rounded-xl border border-slate-800">
                  {[
                    { id: 'PDF', label: 'PDF', icon: FileText },
                    { id: 'CSV', label: 'CSV', icon: FileSpreadsheet },
                    { id: 'URL', label: 'URL', icon: LinkIcon },
                    { id: 'JSON', label: 'JSON', icon: Code },
                    { id: 'PRODUCT_NAME', label: 'Name', icon: Tag }
                  ].map((tab) => {
                    const Icon = tab.icon;
                    const isActive = activeTab === tab.id;
                    return (
                      <button
                        key={tab.id}
                        type="button"
                        onClick={() => handleTabChange(tab.id)}
                        className={`flex flex-col items-center justify-center py-2.5 px-1 rounded-lg text-xs font-semibold transition-all duration-200 ${
                          isActive
                            ? 'bg-indigo-600 text-white shadow-md shadow-indigo-600/30'
                            : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
                        }`}
                      >
                        <Icon className="w-4 h-4 mb-1" />
                        {tab.label}
                      </button>
                    );
                  })}
                </div>
              </div>

              {/* Input Area Form */}
              <form onSubmit={handleSubmit} className="space-y-5">
                <div className="flex items-center justify-between">
                  <label className="block text-xs font-semibold text-slate-400 uppercase tracking-wider">
                    2. Provide Product Data
                  </label>
                  
                  {/* Preset Buttons */}
                  <div className="flex items-center space-x-2">
                    <span className="text-xs text-slate-500">Quick Samples:</span>
                    <button
                      type="button"
                      onClick={() => loadPreset(activeTab)}
                      className="inline-flex items-center text-xs text-indigo-400 hover:text-indigo-300 font-medium hover:underline bg-indigo-500/10 px-2.5 py-1 rounded-md border border-indigo-500/20"
                    >
                      <Sparkles className="w-3 h-3 mr-1" /> Load Preset
                    </button>
                  </div>
                </div>

                {/* PDF Input */}
                {activeTab === 'PDF' && (
                  <div className="space-y-3">
                    <div className="border-2 border-dashed border-slate-700 hover:border-indigo-500/50 rounded-xl p-6 text-center bg-slate-950/50 transition-colors cursor-pointer relative">
                      <input
                        type="file"
                        accept=".pdf"
                        onChange={handleFileChange}
                        className="absolute inset-0 opacity-0 cursor-pointer w-full h-full"
                      />
                      <UploadCloud className="w-10 h-10 text-indigo-400 mx-auto mb-2" />
                      <p className="text-sm font-medium text-slate-200">
                        {file && file.name.toLowerCase().endsWith('.pdf') ? file.name : 'Click or Drag PDF file here'}
                      </p>
                      <p className="text-xs text-slate-500 mt-1">Supports PDF datasheets up to 50MB</p>
                    </div>
                  </div>
                )}

                {/* CSV Input */}
                {activeTab === 'CSV' && (
                  <div className="space-y-3">
                    <div className="border-2 border-dashed border-slate-700 hover:border-indigo-500/50 rounded-xl p-6 text-center bg-slate-950/50 transition-colors cursor-pointer relative">
                      <input
                        type="file"
                        accept=".csv"
                        onChange={handleFileChange}
                        className="absolute inset-0 opacity-0 cursor-pointer w-full h-full"
                      />
                      <FileSpreadsheet className="w-10 h-10 text-emerald-400 mx-auto mb-2" />
                      <p className="text-sm font-medium text-slate-200">
                        {file && file.name.toLowerCase().endsWith('.csv') ? file.name : 'Click or Drag CSV file here'}
                      </p>
                      <p className="text-xs text-slate-500 mt-1">Arbitrary column CSV product catalogs</p>
                    </div>
                  </div>
                )}

                {/* URL Input */}
                {activeTab === 'URL' && (
                  <div className="space-y-3">
                    <div className="relative">
                      <LinkIcon className="absolute left-3.5 top-3.5 w-4 h-4 text-slate-500" />
                      <input
                        type="url"
                        value={url}
                        onChange={(e) => setUrl(e.target.value)}
                        placeholder="https://example.com/product/abb-acs880"
                        className="w-full bg-slate-950 border border-slate-800 rounded-xl pl-10 pr-4 py-3 text-sm text-slate-100 placeholder-slate-600 focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 font-mono"
                      />
                    </div>
                  </div>
                )}

                {/* JSON Input */}
                {activeTab === 'JSON' && (
                  <div className="space-y-3">
                    <textarea
                      rows={8}
                      value={jsonText}
                      onChange={(e) => setJsonText(e.target.value)}
                      placeholder='{\n  "product_name": "SKF 6205",\n  "brand": "SKF",\n  "sku": "6205"\n}'
                      className="w-full bg-slate-950 border border-slate-800 rounded-xl p-4 text-xs font-mono text-indigo-300 placeholder-slate-600 focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 leading-relaxed"
                    />
                  </div>
                )}

                {/* PRODUCT_NAME Input */}
                {activeTab === 'PRODUCT_NAME' && (
                  <div className="space-y-3">
                    <textarea
                      rows={5}
                      value={productName}
                      onChange={(e) => setProductName(e.target.value)}
                      placeholder="Enter raw product title or specs e.g. ABB ACS880 Drive Model ACS880-01-145A-3"
                      className="w-full bg-slate-950 border border-slate-800 rounded-xl p-4 text-sm text-slate-100 placeholder-slate-600 focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 leading-relaxed"
                    />
                  </div>
                )}

                {/* Error Banner */}
                {error && (
                  <div className="p-4 bg-rose-500/10 border border-rose-500/30 rounded-xl flex items-start space-x-3 text-rose-300 text-xs">
                    <AlertCircle className="w-4 h-4 text-rose-400 mt-0.5 shrink-0" />
                    <div>
                      <strong className="font-semibold block text-rose-200">Validation / Processing Error</strong>
                      <span>{error}</span>
                    </div>
                  </div>
                )}

                {/* Submit Action Button */}
                <button
                  type="submit"
                  disabled={loading}
                  className="w-full py-3.5 px-6 rounded-xl bg-gradient-to-r from-indigo-600 to-violet-600 hover:from-indigo-500 hover:to-violet-500 active:scale-[0.99] text-white font-semibold text-sm shadow-lg shadow-indigo-600/30 transition-all flex items-center justify-center space-x-2 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {loading ? (
                    <>
                      <RefreshCw className="w-4 h-4 animate-spin text-white" />
                      <span>Processing Product Input...</span>
                    </>
                  ) : (
                    <>
                      <span>Process Product</span>
                      <ArrowRight className="w-4 h-4 ml-1" />
                    </>
                  )}
                </button>
              </form>
            </div>
          </div>

          {/* Right Panel: Output & Structured Display */}
          <div className="lg:col-span-6 space-y-6">
            {!response && !loading && (
              <div className="bg-slate-900/50 rounded-2xl border border-slate-800/80 p-12 text-center flex flex-col items-center justify-center min-h-[420px]">
                <div className="w-16 h-16 rounded-2xl bg-slate-800/60 flex items-center justify-center text-slate-500 mb-4 border border-slate-700/50">
                  <Box className="w-8 h-8 text-indigo-400/60" />
                </div>
                <h3 className="text-base font-semibold text-slate-300">Ready for Product Intake</h3>
                <p className="text-xs text-slate-500 max-w-sm mt-1">
                  Select an input type on the left panel, upload a document or enter text, and click Process Product.
                </p>
              </div>
            )}

            {loading && (
              <div className="bg-slate-900/90 rounded-2xl border border-slate-800 p-12 text-center flex flex-col items-center justify-center min-h-[420px] space-y-4">
                <div className="relative">
                  <div className="w-16 h-16 rounded-full border-4 border-indigo-500/20 border-t-indigo-500 animate-spin"></div>
                  <Cpu className="w-6 h-6 text-indigo-400 absolute inset-0 m-auto" />
                </div>
                <div>
                  <h3 className="text-base font-semibold text-slate-200">Executing Module 1 Pipeline</h3>
                  <p className="text-xs text-slate-400 mt-1">Validating -&gt; Detecting Type -&gt; Extracting Content & Identity -&gt; Building Standard Object...</p>
                </div>
              </div>
            )}

            {response && (
              <div className="space-y-6">
                
                {/* Result Header Badge */}
                <div className="bg-slate-900/90 rounded-2xl border border-slate-800 p-5 shadow-xl space-y-4">
                  <div className="flex items-center justify-between pb-3 border-b border-slate-800">
                    <div className="flex items-center space-x-3">
                      <span className="px-2.5 py-1 rounded-md text-xs font-bold bg-indigo-500/20 text-indigo-300 border border-indigo-500/30">
                        {response.input_type}
                      </span>
                      <span className="text-xs font-mono text-slate-400">
                        ID: <strong className="text-slate-200">{response.request_id}</strong>
                      </span>
                    </div>
                    <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                      <CheckCircle2 className="w-3.5 h-3.5 mr-1 text-emerald-400" />
                      {response.status}
                    </span>
                  </div>

                  {/* Extracted Identity Summary Cards */}
                  <div>
                    <h4 className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">
                      Extracted Identity
                    </h4>
                    <div className="grid grid-cols-2 gap-2 text-xs">
                      <div className="bg-slate-950 p-2.5 rounded-lg border border-slate-800">
                        <span className="text-slate-500 block">Product Name</span>
                        <strong className="text-indigo-200 truncate block">
                          {response.identity?.product_name || <em className="text-slate-600 font-normal">null</em>}
                        </strong>
                      </div>

                      <div className="bg-slate-950 p-2.5 rounded-lg border border-slate-800">
                        <span className="text-slate-500 block">Brand / Manufacturer</span>
                        <strong className="text-slate-200 truncate block">
                          {response.identity?.brand || response.identity?.manufacturer || <em className="text-slate-600 font-normal">null</em>}
                        </strong>
                      </div>

                      <div className="bg-slate-950 p-2.5 rounded-lg border border-slate-800">
                        <span className="text-slate-500 block">Model</span>
                        <strong className="text-slate-200 truncate block">
                          {response.identity?.model || <em className="text-slate-600 font-normal">null</em>}
                        </strong>
                      </div>

                      <div className="bg-slate-950 p-2.5 rounded-lg border border-slate-800">
                        <span className="text-slate-500 block">SKU / Part Number</span>
                        <strong className="text-slate-200 truncate block">
                          {response.identity?.sku || response.identity?.part_number || <em className="text-slate-600 font-normal">null</em>}
                        </strong>
                      </div>
                    </div>
                  </div>

                  {/* Technical Metadata Bar */}
                  <div className="pt-2 border-t border-slate-800 flex flex-wrap items-center gap-x-4 gap-y-1 text-xs text-slate-400">
                    {response.metadata?.filename && (
                      <span>File: <strong className="text-slate-300">{response.metadata.filename}</strong></span>
                    )}
                    {response.metadata?.size_bytes !== null && response.metadata?.size_bytes !== undefined && (
                      <span>Size: <strong className="text-slate-300">{response.metadata.size_bytes} B</strong></span>
                    )}
                    {response.metadata?.source_url && (
                      <span className="truncate max-w-xs">URL: <strong className="text-indigo-300">{response.metadata.source_url}</strong></span>
                    )}
                  </div>
                </div>

                {/* Formatted JSON Output Viewer */}
                <div className="bg-slate-900/90 rounded-2xl border border-slate-800 p-5 shadow-xl space-y-3">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-2">
                      <Code className="w-4 h-4 text-indigo-400" />
                      <h4 className="text-xs font-semibold text-slate-300 uppercase tracking-wider">
                        Standard Product Input Object (JSON)
                      </h4>
                    </div>

                    <button
                      onClick={copyJsonToClipboard}
                      className="inline-flex items-center space-x-1 text-xs px-2.5 py-1 rounded-md bg-slate-800 hover:bg-slate-700 text-slate-300 border border-slate-700 transition-colors"
                    >
                      {copied ? (
                        <>
                          <Check className="w-3.5 h-3.5 text-emerald-400" />
                          <span className="text-emerald-400">Copied</span>
                        </>
                      ) : (
                        <>
                          <Copy className="w-3.5 h-3.5 text-slate-400" />
                          <span>Copy JSON</span>
                        </>
                      )}
                    </button>
                  </div>

                  <div className="bg-slate-950 rounded-xl p-4 border border-slate-800 max-h-[380px] overflow-auto">
                    <pre className="text-xs font-mono text-indigo-200 leading-relaxed whitespace-pre-wrap break-words">
                      {JSON.stringify(response, null, 2)}
                    </pre>
                  </div>
                </div>

              </div>
            )}
          </div>

        </div>

      </main>

      {/* Footer */}
      <footer className="border-t border-slate-900 bg-slate-950 py-4 px-6 text-center text-xs text-slate-600">
        ProductDNA Intelligence Platform &bull; Module 1 Prototype &bull; Standard Output Saved to <code className="text-slate-500 font-mono">Backend/input_data/Standard_input/</code>
      </footer>
    </div>
  );
}
