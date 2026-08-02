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
  ArrowRight
} from 'lucide-react';

const API_BASE_URL = 'http://localhost:8000/api/product-input';

export default function App() {
  const [activeTab, setActiveTab] = useState('FILE'); // FILE, NAME, URL, JSON
  const [file, setFile] = useState(null);
  const [productName, setProductName] = useState('');
  const [url, setUrl] = useState('');
  const [jsonText, setJsonText] = useState('');

  const [loading, setLoading] = useState(false);
  const [response, setResponse] = useState(null);
  const [error, setError] = useState(null);
  const [copied, setCopied] = useState(false);

  // Preset demo samples
  const loadPreset = (type) => {
    setError(null);
    if (type === 'NAME') {
      setActiveTab('NAME');
      setProductName('ABB ACS880 Drive\n\nSKU:\nACS880-01-145A-3\n\nBrand ABB');
    } else if (type === 'URL') {
      setActiveTab('URL');
      setUrl('https://www.abb.com');
    } else if (type === 'JSON') {
      setActiveTab('JSON');
      setJsonText(JSON.stringify({
        product_name: "Schneider Electric Altivar 320",
        brand: "Schneider Electric",
        sku: "ATV320U15N4B",
        model: "ATV320",
        voltage: "400V 3-Phase",
        power_rating: "1.5 kW"
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
      if (activeTab === 'FILE') {
        if (!file) {
          throw new Error('Please select a file (.pdf or .csv) to upload.');
        }
        const formData = new FormData();
        formData.append('file', file);
        res = await axios.post(API_BASE_URL, formData, {
          headers: { 'Content-Type': 'multipart/form-data' }
        });
      } else if (activeTab === 'NAME') {
        if (!productName.trim()) {
          throw new Error('Please enter a product name or details.');
        }
        const formData = new FormData();
        formData.append('input_text', productName);
        res = await axios.post(API_BASE_URL, formData);
      } else if (activeTab === 'URL') {
        if (!url.trim()) {
          throw new Error('Please enter a URL.');
        }
        const formData = new FormData();
        formData.append('input_text', url);
        res = await axios.post(API_BASE_URL, formData);
      } else if (activeTab === 'JSON') {
        if (!jsonText.trim()) {
          throw new Error('Please enter JSON text.');
        }
        let parsed;
        try {
          parsed = JSON.parse(jsonText);
        } catch (err) {
          throw new Error('Invalid JSON string syntax.');
        }
        res = await axios.post(API_BASE_URL, { json_data: parsed });
      }

      setResponse(res.data);
    } catch (err) {
      if (err.response && err.response.data && err.response.data.detail) {
        setError(err.response.data.detail);
      } else {
        setError(err.message || 'An error occurred while submitting product input.');
      }
    } finally {
      setLoading(false);
    }
  };

  const handleCopyJson = () => {
    if (response) {
      navigator.clipboard.writeText(JSON.stringify(response, null, 2));
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  return (
    <div className="min-h-screen bg-gray-950 text-gray-100 flex flex-col font-sans selection:bg-blue-600 selection:text-white">
      {/* Header */}
      <header className="border-b border-gray-800 bg-gray-900/80 backdrop-blur sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="h-10 w-10 rounded-xl bg-gradient-to-tr from-blue-600 to-indigo-500 flex items-center justify-center shadow-lg shadow-blue-500/20">
              <Cpu className="h-5 w-5 text-white" />
            </div>
            <div>
              <h1 className="text-xl font-bold tracking-tight text-white flex items-center gap-2">
                Product<span className="text-blue-500">DNA</span>
                <span className="text-xs px-2 py-0.5 rounded-full bg-blue-500/10 text-blue-400 border border-blue-500/20 font-mono font-medium"> abc </span>
              </h1>
              <p className="text-xs text-gray-400">Product Intake & Document Processing Engine</p>
            </div>
          </div>

          <div className="hidden sm:flex items-center gap-2">
            <span className="text-xs text-gray-400 bg-gray-800 px-3 py-1.5 rounded-lg border border-gray-700 font-mono">
              Deterministic Parsing • Zero AI
            </span>
          </div>
        </div>
      </header>

      {/* Main Grid */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8 grid grid-cols-1 lg:grid-cols-12 gap-8">

        {/* Left Column: Form */}
        <div className="lg:col-span-6 flex flex-col space-y-6">
          <div className="bg-gray-900 border border-gray-800 rounded-2xl p-6 shadow-xl relative overflow-hidden">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-lg font-semibold text-white flex items-center gap-2">
                <UploadCloud className="h-5 w-5 text-blue-400" />
                Upload Product Input
              </h2>
              <span className="text-xs text-gray-400">Select 1 Input Method</span>
            </div>

            {/* Tabs */}
            <div className="grid grid-cols-4 gap-2 p-1.5 bg-gray-950 rounded-xl border border-gray-800 mb-6">
              <button
                type="button"
                onClick={() => setActiveTab('FILE')}
                className={`flex items-center justify-center gap-1.5 py-2.5 px-3 rounded-lg text-xs font-medium transition-all ${activeTab === 'FILE'
                  ? 'bg-blue-600 text-white shadow-md'
                  : 'text-gray-400 hover:text-gray-200 hover:bg-gray-800'
                  }`}
              >
                <FileText className="h-4 w-4" />
                File
              </button>

              <button
                type="button"
                onClick={() => setActiveTab('NAME')}
                className={`flex items-center justify-center gap-1.5 py-2.5 px-3 rounded-lg text-xs font-medium transition-all ${activeTab === 'NAME'
                  ? 'bg-blue-600 text-white shadow-md'
                  : 'text-gray-400 hover:text-gray-200 hover:bg-gray-800'
                  }`}
              >
                <Tag className="h-4 w-4" />
                Name
              </button>

              <button
                type="button"
                onClick={() => setActiveTab('URL')}
                className={`flex items-center justify-center gap-1.5 py-2.5 px-3 rounded-lg text-xs font-medium transition-all ${activeTab === 'URL'
                  ? 'bg-blue-600 text-white shadow-md'
                  : 'text-gray-400 hover:text-gray-200 hover:bg-gray-800'
                  }`}
              >
                <LinkIcon className="h-4 w-4" />
                URL
              </button>

              <button
                type="button"
                onClick={() => setActiveTab('JSON')}
                className={`flex items-center justify-center gap-1.5 py-2.5 px-3 rounded-lg text-xs font-medium transition-all ${activeTab === 'JSON'
                  ? 'bg-blue-600 text-white shadow-md'
                  : 'text-gray-400 hover:text-gray-200 hover:bg-gray-800'
                  }`}
              >
                <Code className="h-4 w-4" />
                JSON
              </button>
            </div>

            {/* Inputs */}
            <form onSubmit={handleSubmit} className="space-y-5">
              {activeTab === 'FILE' && (
                <div className="space-y-2">
                  <label className="block text-xs font-medium text-gray-300">
                    Upload PDF or CSV Document
                  </label>
                  <div className="border-2 border-dashed border-gray-700 hover:border-blue-500 transition-colors rounded-xl p-6 text-center bg-gray-950/50 cursor-pointer relative group">
                    <input
                      type="file"
                      accept=".pdf,.csv,.png,.jpg,.jpeg"
                      onChange={handleFileChange}
                      className="absolute inset-0 w-full h-full opacity-0 cursor-pointer z-10"
                    />
                    <div className="flex flex-col items-center justify-center space-y-2">
                      <div className="p-3 bg-gray-800 rounded-full group-hover:bg-blue-600/20 text-blue-400 transition-colors">
                        <UploadCloud className="h-6 w-6" />
                      </div>
                      {file ? (
                        <div className="text-sm font-medium text-blue-400">
                          {file.name} ({(file.size / 1024).toFixed(1)} KB)
                        </div>
                      ) : (
                        <>
                          <p className="text-sm font-medium text-gray-300">
                            Click or drag file to upload
                          </p>
                          <p className="text-xs text-gray-500">
                            Supports PDF, CSV, PNG, JPG
                          </p>
                        </>
                      )}
                    </div>
                  </div>
                </div>
              )}

              {activeTab === 'NAME' && (
                <div className="space-y-2">
                  <label className="block text-xs font-medium text-gray-300">
                    Product Name & Spec Details
                  </label>
                  <textarea
                    rows={6}
                    value={productName}
                    onChange={(e) => setProductName(e.target.value)}
                    placeholder="Enter Product Name, Brand, SKU, Model details..."
                    className="w-full bg-gray-950 border border-gray-800 rounded-xl p-3 text-sm text-gray-100 placeholder-gray-600 focus:outline-none focus:border-blue-500 font-mono transition-colors"
                  />
                </div>
              )}

              {activeTab === 'URL' && (
                <div className="space-y-2">
                  <label className="block text-xs font-medium text-gray-300">
                    Product Web Page URL
                  </label>
                  <input
                    type="url"
                    value={url}
                    onChange={(e) => setUrl(e.target.value)}
                    placeholder="https://example.com/product/acs880"
                    className="w-full bg-gray-950 border border-gray-800 rounded-xl p-3 text-sm text-gray-100 placeholder-gray-600 focus:outline-none focus:border-blue-500 font-mono transition-colors"
                  />
                </div>
              )}

              {activeTab === 'JSON' && (
                <div className="space-y-2">
                  <label className="block text-xs font-medium text-gray-300">
                    Raw Product JSON Payload
                  </label>
                  <textarea
                    rows={8}
                    value={jsonText}
                    onChange={(e) => setJsonText(e.target.value)}
                    placeholder='{\n  "product_name": "ABB ACS880 Drive",\n  "sku": "ACS880-01-145A-3"\n}'
                    className="w-full bg-gray-950 border border-gray-800 rounded-xl p-3 text-sm text-gray-100 placeholder-gray-600 focus:outline-none focus:border-blue-500 font-mono transition-colors"
                  />
                </div>
              )}

              <button
                type="submit"
                disabled={loading}
                className="w-full bg-blue-600 hover:bg-blue-500 text-white font-medium py-3 px-4 rounded-xl transition-all shadow-lg shadow-blue-600/20 flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {loading ? (
                  <>
                    <div className="h-4 w-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                    <span>Processing Intake...</span>
                  </>
                ) : (
                  <>
                    <span>Submit to Intake Pipeline</span>
                    <ArrowRight className="h-4 w-4" />
                  </>
                )}
              </button>
            </form>

            {/* Demo Presets */}
            <div className="mt-6 pt-6 border-t border-gray-800">
              <p className="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-3 flex items-center gap-1.5">
                <Sparkles className="h-3.5 w-3.5 text-blue-400" />
                Quick Demo Presets
              </p>
              <div className="flex flex-wrap gap-2">
                <button
                  type="button"
                  onClick={() => loadPreset('NAME')}
                  className="text-xs bg-gray-800 hover:bg-gray-750 text-gray-300 px-3 py-1.5 rounded-lg border border-gray-700 transition-colors"
                >
                  ABB Drive Sample
                </button>
                <button
                  type="button"
                  onClick={() => loadPreset('JSON')}
                  className="text-xs bg-gray-800 hover:bg-gray-750 text-gray-300 px-3 py-1.5 rounded-lg border border-gray-700 transition-colors"
                >
                  Schneider JSON Sample
                </button>
                <button
                  type="button"
                  onClick={() => loadPreset('URL')}
                  className="text-xs bg-gray-800 hover:bg-gray-750 text-gray-300 px-3 py-1.5 rounded-lg border border-gray-700 transition-colors"
                >
                  ABB URL Sample
                </button>
              </div>
            </div>
          </div>
        </div>

        {/* Right Column: Output JSON */}
        <div className="lg:col-span-6 flex flex-col space-y-6">
          <div className="bg-gray-900 border border-gray-800 rounded-2xl p-6 shadow-xl flex-1 flex flex-col relative">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-semibold text-white flex items-center gap-2">
                <Code className="h-5 w-5 text-blue-400" />
                Standard Product Input Object
              </h2>
              {response && (
                <button
                  onClick={handleCopyJson}
                  className="flex items-center gap-1 text-xs bg-gray-800 hover:bg-gray-700 text-gray-300 px-2.5 py-1.5 rounded-lg border border-gray-700 transition-colors"
                >
                  {copied ? (
                    <>
                      <Check className="h-3.5 w-3.5 text-green-400" />
                      <span className="text-green-400">Copied</span>
                    </>
                  ) : (
                    <>
                      <Copy className="h-3.5 w-3.5" />
                      <span>Copy JSON</span>
                    </>
                  )}
                </button>
              )}
            </div>

            {error && (
              <div className="bg-red-500/10 border border-red-500/20 text-red-400 p-4 rounded-xl text-sm flex items-start gap-3 mb-4">
                <AlertCircle className="h-5 w-5 text-red-400 shrink-0 mt-0.5" />
                <div>
                  <p className="font-semibold">Processing Failure</p>
                  <p className="text-xs text-red-300/90 mt-0.5">{error}</p>
                </div>
              </div>
            )}

            {response && response.identity && (
              <div className="grid grid-cols-2 gap-3 mb-4 bg-gray-950/60 p-3 rounded-xl border border-gray-800">
                <div className="space-y-0.5">
                  <span className="text-[10px] uppercase font-bold text-gray-500">Product Name</span>
                  <p className="text-xs font-semibold text-blue-300 truncate">
                    {response.identity.product_name || 'N/A'}
                  </p>
                </div>
                <div className="space-y-0.5">
                  <span className="text-[10px] uppercase font-bold text-gray-500">Brand</span>
                  <p className="text-xs font-semibold text-gray-200 truncate">
                    {response.identity.brand || 'N/A'}
                  </p>
                </div>
                <div className="space-y-0.5">
                  <span className="text-[10px] uppercase font-bold text-gray-500">SKU</span>
                  <p className="text-xs font-semibold font-mono text-emerald-400 truncate">
                    {response.identity.sku || 'N/A'}
                  </p>
                </div>
                <div className="space-y-0.5">
                  <span className="text-[10px] uppercase font-bold text-gray-500">Model</span>
                  <p className="text-xs font-semibold text-gray-200 truncate">
                    {response.identity.model || 'N/A'}
                  </p>
                </div>
              </div>
            )}

            <div className="flex-1 bg-gray-950 border border-gray-800 rounded-xl p-4 overflow-auto max-h-[500px]">
              {response ? (
                <pre className="text-xs font-mono text-gray-200 whitespace-pre-wrap leading-relaxed">
                  {JSON.stringify(response, null, 2)}
                </pre>
              ) : (
                <div className="h-full min-h-[300px] flex flex-col items-center justify-center text-gray-600 space-y-3">
                  <Code className="h-10 w-10 stroke-1" />
                  <p className="text-xs text-gray-500 text-center max-w-xs">
                    Submit an input payload on the left to see the generated Standard Product Input Object JSON.
                  </p>
                </div>
              )}
            </div>
          </div>
        </div>

      </main>

      <footer className="border-t border-gray-900 bg-gray-950 py-4 text-center text-xs text-gray-500">
        ProductDNA Intelligence Platform • Module 1 Product Intake Pipeline
      </footer>
    </div>
  );
}
