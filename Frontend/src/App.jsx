import React, { useState, useEffect } from 'react';
import axios from 'axios';
import {
  FileText,
  UploadCloud,
  AlertCircle,
  Copy,
  Check,
  Cpu,
  FileSpreadsheet,
  Box,
  RefreshCw,
  Code,
  Download,
  CheckCircle2,
  Tag,
  ExternalLink,
  Layers,
  Sparkles,
  Plus,
  Trash2,
  Info,
  Database,
  Globe,
  FileCode,
  CheckSquare,
  Search
} from 'lucide-react';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000';
const MODULE1_API_URL = `${API_BASE_URL}/api/product-input`;
const RESOURCES_API_URL = `${API_BASE_URL}/api/resources`;

const STATIC_PRODUCT_OUTPUT = {
  "MFR URL": "https://www.frigidaire.com/en/p/owner-center/product-support/PDSH4816AF",
  "PART_NUMBER": "20887830",
  "Dept": "Appliances",
  "Class": "Large Appliances",
  "Fine": "Dishwashers",
  "SKU - MY_PART_NUMBER": "1515863",
  "Mfg_Part_Num": "PDSH4816AF",
  "Part_Desc": "PDSH4816AF Dishwasher SS - Display Only",
  "E1_Brand": "-- Unbranded --",
  "Unilog_Brand": "-- No Unilog Brand --",
  "DIB_Brand": "-- No DIB Brand --",
  "Part_Manuf": "Appliance Dealers Cooperative (APPDE)",
  "MANUFACTURER_NAME": "Rheem Manufacturing",
  "BRAND_NAME": "FRIGIDAIRE®",
  "MANUFACTURER_PART_NUMBER": "PDSH4816AF",
  "Classpath": "Appliances & Consumer Electronics>Kitchen Appliances>Built-In Dishwashers",
  "MOBILE_DESC": "Rheem Manufacturing FRIGIDAIRE, Dishwasher, Professional Series, PDSH4816AF",
  "INVOICE_DESC": "DISHWASHER LEG 5 SST 120V 15A 50-1/4IN",
  "SHORT_DESC": "FRIGIDAIRE® Professional Series PDSH4816AF Dishwasher With CleanBoost™, Leg Mounting, 5-Wash Cycle, Stainless Steel",
  "LONG_DESC1": "FRIGIDAIRE® Dishwasher With CleanBoost™, Professional Series, 5 Wash Cycles, 120 V, 15 A, Leg Mounting, 24 in W x 24-1/4 in D, 50-1/4 in Depth With Door Open, 8-1/2 in Upper Rack, 11-1/4 in Lower Rack Minimum Height, 10-3/8 in Upper Rack, 13-1/4 in Lower Rack Maximum Height, 47 dBA Sound Level, Stainless Steel, Additional Information: 240 kW-hr Annual Energy, 1 to 12 hr Delay Start Hours",
  "RETAIL_DESC": "Professional Series Dishwasher, Leg Mounting, 5-Wash Cycle, Stainless Steel",
  "With": "With CleanBoost™",
  "Standard/Approvals": "ASSE 1006|CEE Tier 2 Qualified|cUL Listed|ENERGY STAR Certified|NSF Certified|UL Listed",
  "Product Name": "Dishwasher",

  "ATTRIBUTE_LABEL 1": "Series",
  "ATTRIBUTE_VALUE 1": "Professional Series",

  "ATTRIBUTE_LABEL 2": "Model",
  "ATTRIBUTE_VALUE 2": "",

  "ATTRIBUTE_LABEL 3": "Number of Wash Cycles",
  "ATTRIBUTE_VALUE 3": "5",

  "ATTRIBUTE_LABEL 4": "Voltage Rating",
  "ATTRIBUTE_VALUE 4": "120",
  "ATTRIBUTE_UOM 4": "V",

  "ATTRIBUTE_LABEL 5": "Amperage Rating",
  "ATTRIBUTE_VALUE 5": "15",
  "ATTRIBUTE_UOM 5": "A",

  "ATTRIBUTE_LABEL 6": "Mounting Type",
  "ATTRIBUTE_VALUE 6": "Leg",

  "ATTRIBUTE_LABEL 7": "Plug Type",
  "ATTRIBUTE_VALUE 7": "",

  "ATTRIBUTE_LABEL 8": "Size",
  "ATTRIBUTE_VALUE 8": "24 in W x 24-1/4 in D",

  "ATTRIBUTE_LABEL 9": "Depth With Door Open",
  "ATTRIBUTE_VALUE 9": "50-1/4",
  "ATTRIBUTE_UOM 9": "in",

  "ATTRIBUTE_LABEL 10": "Minimum Height",
  "ATTRIBUTE_VALUE 10": "8-1/2 in Upper Rack, 11-1/4 in Lower Rack",

  "ATTRIBUTE_LABEL 11": "Maximum Height",
  "ATTRIBUTE_VALUE 11": "10-3/8 in Upper Rack, 13-1/4 in Lower Rack",

  "ATTRIBUTE_LABEL 12": "Sound Level",
  "ATTRIBUTE_VALUE 12": "47",
  "ATTRIBUTE_UOM 12": "dBA",

  "ATTRIBUTE_LABEL 13": "Material",
  "ATTRIBUTE_VALUE 13": "Stainless Steel",

  "ATTRIBUTE_LABEL 14": "Color",
  "ATTRIBUTE_VALUE 14": "",

  "ATTRIBUTE_LABEL 15": "Additional Information",
  "ATTRIBUTE_VALUE 15": "240 kW-hr Annual Energy, 1 to 12 hr Delay Start Hours",

  "Warranty": "1 Year Manufacturer, 1 Year Labor and Parts",

  "Product Image": "FRIGIDAIRE_PDSH4816AF.jpg",
  "Alternate Image 1": "FRIGIDAIRE_PDSH4816AF_1.jpg",
  "Alternate Image 2": "FRIGIDAIRE_PDSH4816AF_2.jpg",
  "Alternate Image 3": "FRIGIDAIRE_PDSH4816AF_3.jpg",
  "Alternate Image 4": "FRIGIDAIRE_PDSH4816AF_4.jpg",

  "Specification Sheet": "FRIGIDAIRE_PDSH4816AF_Specification_Sheet.pdf",
  "Actual Image (Yes/No)": "Yes"
};

export default function App() {
  // --- MODULE 1 STATE ---
  const [m1Tab, setM1Tab] = useState('CSV');
  const [m1File, setM1File] = useState(null);
  const [m1Loading, setM1Loading] = useState(false);
  const [m1Response, setM1Response] = useState(null);
  const [m1RawResponse, setM1RawResponse] = useState(null);
  const [m1DetectedHeaders, setM1DetectedHeaders] = useState([]);
  const [m1Error, setM1Error] = useState(null);
  const [m1Copied, setM1Copied] = useState(false);
  const [viewMode, setViewMode] = useState('SUMMARY'); // 'SUMMARY' or 'JSON'

  // --- PRODUCT SELECTOR STATE ---
  const [module1Products, setModule1Products] = useState([]);
  const [selectedProductId, setSelectedProductId] = useState(null);
  const [selectedProduct, setSelectedProduct] = useState(null);
  const [productSearchTerm, setProductSearchTerm] = useState('');
  const [orgRegistry, setOrgRegistry] = useState([]);
  const [productsLoading, setProductsLoading] = useState(false);
  const [selectedProductLoading, setSelectedProductLoading] = useState(false);
  const [processSelectedLoading, setProcessSelectedLoading] = useState(false);
  const [processSelectedSuccess, setProcessSelectedSuccess] = useState(null);
  const [productsError, setProductsError] = useState(null);

  // --- MODULE 5 STATE ---
  const [m5Loading, setM5Loading] = useState(false);
  const [m5Result, setM5Result] = useState(null);
  const [m5Error, setM5Error] = useState(null);
  const [m5Show252, setM5Show252] = useState(false);

  // --- MODULE 2 PRODUCT RESOURCES STATE ---
  const [activeRequestId, setActiveRequestId] = useState('REQ-20260831-001');
  const [resources, setResources] = useState([]);
  const [resTab, setResTab] = useState('PDF'); // 'PDF', 'URL', 'TEXT'
  const [resFile, setResFile] = useState(null);
  const [resUrl, setResUrl] = useState('');
  const [resText, setResText] = useState('');
  const [resName, setResName] = useState('');
  const [resLoading, setResLoading] = useState(false);
  const [resError, setResError] = useState(null);
  const [selectedResource, setSelectedResource] = useState(null);

  // Global Detailed API Error Diagnostic State
  const [globalApiError, setGlobalApiError] = useState(null);

  const formatDetailedError = (err, actionName, targetUrl) => {
    const target = targetUrl || API_BASE_URL;
    const message = err.message || 'Unknown Error';
    const code = err.code || '';
    const status = err.response?.status ? `HTTP ${err.response.status} ${err.response.statusText || ''}` : 'No Response (Network Error)';
    let responseData = null;
    if (err.response?.data) {
      responseData = typeof err.response.data === 'object' ? JSON.stringify(err.response.data, null, 2) : String(err.response.data);
    }
    
    let explanation = '';
    if (err.message === 'Network Error' || !err.response) {
      explanation = `Unable to connect to backend at "${target}".\n• If running on Vercel: Set VITE_API_URL in Vercel settings to a public HTTPS URL (e.g. Ngrok or Render).\n• If running locally: Ensure FastAPI backend (uvicorn main:app --reload) is running on port 8000.`;
    }

    return {
      action: actionName,
      targetUrl: target,
      message,
      code,
      status,
      responseData,
      explanation
    };
  };

  // Fetch Module 1 Products List
  const fetchModule1Products = async () => {
    setProductsLoading(true);
    setProductsError(null);
    try {
      const res = await axios.get(`${API_BASE_URL}/api/products/module1`);
      if (res.data && Array.isArray(res.data.products)) {
        setModule1Products(res.data.products);
        if (res.data.products.length > 0 && !selectedProductId) {
          setSelectedProductId(res.data.products[0].product_id);
        }
        setGlobalApiError(null);
      }
    } catch (err) {
      console.warn("Could not fetch Module 1 products list:", err);
      const detailed = formatDetailedError(err, "Fetch Module 1 Products List", `${API_BASE_URL}/api/products/module1`);
      setProductsError(detailed.message);
      setGlobalApiError(detailed);
    } finally {
      setProductsLoading(false);
    }
  };

  // Fetch Resources from Backend
  const fetchResources = async (reqId) => {
    try {
      const target = `${RESOURCES_API_URL}?request_id=${reqId || activeRequestId}`;
      const response = await axios.get(target);
      if (Array.isArray(response.data)) {
        setResources(response.data);
      }
    } catch (err) {
      console.warn("Could not connect to FastAPI /api/resources, using local empty resources list.", err);
      if (!globalApiError) {
        setGlobalApiError(formatDetailedError(err, "Fetch Product Resources", RESOURCES_API_URL));
      }
    }
  };

  useEffect(() => {
    fetchResources(activeRequestId);
  }, [activeRequestId]);

  // Fetch full details of selected product and automatically process it
  useEffect(() => {
    if (!selectedProductId) {
      setSelectedProduct(null);
      return;
    }
    const loadAndProcessProductDetails = async () => {
      setSelectedProductLoading(true);
      setProcessSelectedLoading(true);
      setProcessSelectedSuccess(null);
      try {
        // 1. Load details
        const res = await axios.get(`${API_BASE_URL}/api/products/module1/${selectedProductId}`);
        setSelectedProduct(res.data);
        
        // 2. Automatically process selected product for downstream
        const processRes = await axios.post(`${API_BASE_URL}/api/products/process-selected`, {
          product_id: selectedProductId
        });
        
        if (processRes.data && processRes.data.status === 'SUCCESS') {
          setProcessSelectedSuccess(`Product ${selectedProductId} loaded for downstream processing!`);
          setActiveRequestId(selectedProductId);
          fetchResources(selectedProductId);
          
          const prod = processRes.data.product;
          if (prod) {
            const raw = prod.source_record?.raw || {};
            const displayObj = {
              PART_NUMBER: raw.PART_NUMBER || raw.Mfg_Part_Num || prod.identity?.part_number || '',
              BRAND_NAME: raw.BRAND_NAME || raw.E1_Brand || prod.identity?.brand || '',
              MANUFACTURER_NAME: raw.MANUFACTURER_NAME || raw.Part_Manuf || prod.identity?.manufacturer || '',
              "SKU - MY_PART_NUMBER": raw["SKU - MY_PART_NUMBER"] || prod.identity?.sku || '',
              SHORT_DESC: raw.SHORT_DESC || raw.Part_Desc || prod.identity?.product_name || 'Unknown Product',
              Dept: raw.Dept || '',
              Class: raw.Class || '',
              Fine: raw.Fine || '',
              ...raw
            };
            setM1Response(displayObj);
            setM1RawResponse(prod);
          }
        }
      } catch (err) {
        console.error("Failed to load or process selected product details:", err);
        setSelectedProduct(null);
        setGlobalApiError(formatDetailedError(err, "Load & Process Product Details", `${API_BASE_URL}/api/products/module1/${selectedProductId}`));
      } finally {
        setSelectedProductLoading(false);
        setProcessSelectedLoading(false);
      }
    };
    loadAndProcessProductDetails();
  }, [selectedProductId]);

  // Initial load for products and registry
  useEffect(() => {
    fetchModule1Products();
    const fetchRegistry = async () => {
      try {
        const res = await axios.get(`${API_BASE_URL}/api/product-registry`);
        if (res.data && Array.isArray(res.data.registry)) {
          setOrgRegistry(res.data.registry);
        }
      } catch (err) {
        console.warn("Could not load organization product registry:", err);
      }
    };
    fetchRegistry();
  }, []);

  // Module 5 — Semantic Interpretation Handler
  const handleRunModule5 = async () => {
    if (!selectedProduct) return;
    setM5Loading(true);
    setM5Error(null);
    setM5Result(null);
    setM5Show252(false);
    try {
      const res = await axios.post(`${API_BASE_URL}/api/module5/semantic-interpretation`, {
        product: selectedProduct,
        organization: orgRegistry.length > 0 ? { records: orgRegistry } : null,
      });
      setM5Result(res.data);
      setGlobalApiError(null);
    } catch (err) {
      const detailed = formatDetailedError(err, "Module 5 Semantic Interpretation", `${API_BASE_URL}/api/module5/semantic-interpretation`);
      setM5Error(`${detailed.message} (${detailed.status})`);
      setGlobalApiError(detailed);
    } finally {
      setM5Loading(false);
    }
  };

  // Format value display helper (Rule 10)
  const formatValue = (val) => {
    if (val === null || val === undefined || String(val).trim() === '' || String(val) === 'null' || String(val) === 'undefined' || String(val) === 'NaN') {
      return <span className="text-slate-500 italic">Not available</span>;
    }
    return val;
  };

  const handleCsvFileChange = (e) => {
    const file = e.target.files?.[0];
    setM1File(file || null);
    setM1Response(null);
    setM1RawResponse(null);
    setM1Error(null);
    if (file) {
      const reader = new FileReader();
      reader.onload = (evt) => {
        const text = evt.target?.result;
        if (typeof text === 'string') {
          const firstLine = text.split('\n')[0];
          const headers = firstLine.split(',').map(h => h.trim().replace(/^["']|["']$/g, '')).filter(Boolean);
          setM1DetectedHeaders(headers);
        }
      };
      reader.readAsText(file.slice(0, 4096));
    } else {
      setM1DetectedHeaders([]);
    }
  };

  // Module 1 Submit Handler
  const handleM1Submit = async (e) => {
    e.preventDefault();
    setM1Loading(true);
    setM1Error(null);

    try {
      if (!m1File && (m1Tab === 'CSV' || m1Tab === 'PDF')) {
        const expectedExt = m1Tab.toLowerCase();
        throw new Error(`Please select or upload a valid .${expectedExt} file.`);
      }

      try {
        const formData = new FormData();
        formData.append('file', m1File);
        formData.append('input_type', m1Tab);
        const res = await axios.post(MODULE1_API_URL, formData, {
          headers: { 'Content-Type': 'multipart/form-data' }
        });
        
        if (res && res.data && res.data.status !== 'ERROR') {
          setM1RawResponse(res.data);
          
          let displayObj = {};
          if (res.data.status === 'SUCCESS' && res.data.items && res.data.items.length > 0) {
            const firstItem = res.data.items[0];
            displayObj = firstItem.source_record?.raw || {};
            displayObj = {
              PART_NUMBER: displayObj.PART_NUMBER || firstItem.identity?.part_number || '',
              BRAND_NAME: displayObj.BRAND_NAME || firstItem.identity?.brand || '',
              MANUFACTURER_NAME: displayObj.MANUFACTURER_NAME || firstItem.identity?.manufacturer || '',
              "SKU - MY_PART_NUMBER": displayObj["SKU - MY_PART_NUMBER"] || firstItem.identity?.sku || '',
              SHORT_DESC: displayObj.SHORT_DESC || displayObj.Part_Desc || firstItem.identity?.product_name || '',
              Dept: displayObj.Dept || '',
              Class: displayObj.Class || '',
              Fine: displayObj.Fine || '',
              ...displayObj
            };
          } else {
             const item = res.data;
             displayObj = {
              PART_NUMBER: item.identity?.part_number || '',
              BRAND_NAME: item.identity?.brand || '',
              MANUFACTURER_NAME: item.identity?.manufacturer || '',
              "SKU - MY_PART_NUMBER": item.identity?.sku || '',
              SHORT_DESC: item.identity?.product_name || item.unstructured_data?.title || 'Unknown Product',
              Dept: '',
              Class: '',
              Fine: ''
            };
          }
          setM1Response(displayObj);
          await fetchModule1Products();
        } else {
          throw new Error(res?.data?.error || 'Unknown server error');
        }
      } catch (backendErr) {
        throw new Error(backendErr.response?.data?.error || backendErr.message || 'Error processing product input.');
      }
    } catch (err) {
      setM1Error(err.message || 'Error processing product input.');
      setM1Response(null);
      setM1RawResponse(null);
    } finally {
      setM1Loading(false);
    }
  };

  // Module 2 Resource Submit Handler
  const handleAddResource = async (e) => {
    e.preventDefault();
    setResLoading(true);
    setResError(null);

    try {
      const formData = new FormData();
      formData.append('request_id', activeRequestId);
      formData.append('type', resTab.toLowerCase());
      formData.append('name', resName || (resFile ? resFile.name : resUrl || 'Product Resource'));
      formData.append('subtype', resTab === 'PDF' ? 'technical_datasheet' : resTab === 'URL' ? 'website' : 'technical_notes');

      if (resTab === 'PDF') {
        if (!resFile) throw new Error('Please select a PDF file to upload.');
        formData.append('file', resFile);
      } else if (resTab === 'URL') {
        if (!resUrl.trim()) throw new Error('Please enter a valid URL.');
        formData.append('value', resUrl.trim());
      } else if (resTab === 'TEXT') {
        if (!resText.trim()) throw new Error('Please enter text content.');
        formData.append('value', resText.trim());
      }

      const res = await axios.post(RESOURCES_API_URL, formData);

      if (res.data) {
        // Reset form
        setResFile(null);
        setResUrl('');
        setResText('');
        setResName('');
        // Refresh resources list
        await fetchResources(activeRequestId);
      }
    } catch (err) {
      const msg = err.response?.data?.detail || err.message || 'Failed to add resource.';
      setResError(msg);
    } finally {
      setResLoading(false);
    }
  };

  // Delete Resource Handler
  const handleDeleteResource = async (sourceId) => {
    try {
      await axios.delete(`${RESOURCES_API_URL}/${sourceId}`);
      await fetchResources(activeRequestId);
      if (selectedResource?.source_id === sourceId) {
        setSelectedResource(null);
      }
    } catch (err) {
      alert(`Failed to delete resource: ${err.response?.data?.detail || err.message}`);
    }
  };

  // CSV Generator and Downloader
  const handleDownloadCsv = () => {
    let dataToDownload = m1Response;
    let fileName = `StandardProductInput_${m1Response?.PART_NUMBER || 'Output'}.csv`;

    if (m5Result && m5Result.delivery_record) {
      dataToDownload = m5Result.delivery_record;
      fileName = `ProductDNA_Output_${selectedProductId || 'Record'}.csv`;
    } else if (!m1Response) {
      return;
    }

    const headers = Object.keys(dataToDownload);
    const values = Object.values(dataToDownload).map(val => {
      const stringVal = val === null || val === undefined ? '' : String(val);
      if (stringVal.includes(',') || stringVal.includes('"') || stringVal.includes('\n')) {
        return `"${stringVal.replace(/"/g, '""')}"`;
      }
      return stringVal;
    });

    const csvContent = headers.join(',') + '\n' + values.join(',');
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.setAttribute('href', url);
    link.setAttribute('download', fileName);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  // Helper to extract attribute rows 1 to 15
  const getAttributesList = (data) => {
    const attrs = [];
    for (let i = 1; i <= 15; i++) {
      const label = data[`ATTRIBUTE_LABEL ${i}`];
      const val = data[`ATTRIBUTE_VALUE ${i}`];
      const uom = data[`ATTRIBUTE_UOM ${i}`];
      if (label || val) {
        attrs.push({
          id: i,
          label: label || `Attribute ${i}`,
          value: val || '-',
          uom: uom || ''
        });
      }
    }
    return attrs;
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col font-sans selection:bg-indigo-500 selection:text-white">
      {/* Top Header */}
      <header className="border-b border-slate-800 bg-slate-900/90 backdrop-blur-md sticky top-0 z-50 px-6 py-3.5">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-indigo-600 via-violet-600 to-indigo-400 flex items-center justify-center shadow-lg shadow-indigo-500/20">
              <Cpu className="w-5 h-5 text-white" />
            </div>
            <div>
              <h1 className="text-lg font-bold bg-clip-text text-transparent bg-gradient-to-r from-white via-slate-200 to-indigo-300">
                ProductDNA Platform
              </h1>
              <p className="text-xs text-slate-400 font-medium tracking-wide">Intelligent Product Resolution & Semantic Enrichment</p>
            </div>
          </div>

          <div className="flex items-center space-x-2">
            <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
              <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse mr-2"></span>
              Backend Ready 
            </span>
          </div>
        </div>
      </header>

      {/* Main Content Area */}
      <main className="flex-1 max-w-7xl w-full mx-auto p-6 space-y-8">

        {/* FULL ERROR DIAGNOSTIC BANNER */}
        {globalApiError && (
          <div className="bg-rose-950/40 border-2 border-rose-500/50 rounded-2xl p-5 shadow-2xl space-y-3 relative overflow-hidden backdrop-blur-md">
            <div className="flex items-start justify-between gap-4">
              <div className="flex items-start space-x-3">
                <div className="p-2 rounded-xl bg-rose-500/20 text-rose-400 border border-rose-500/30 shrink-0 mt-0.5">
                  <AlertCircle className="w-5 h-5" />
                </div>
                <div>
                  <div className="flex items-center space-x-2">
                    <h3 className="text-sm font-bold text-rose-200 uppercase tracking-wider">
                      Network / API Connection Error
                    </h3>
                    <span className="px-2 py-0.5 rounded text-[10px] font-mono font-bold bg-rose-500/20 text-rose-300 border border-rose-500/30">
                      {globalApiError.status}
                    </span>
                  </div>
                  <p className="text-xs text-rose-300 font-semibold mt-1">
                    Failed Action: {globalApiError.action}
                  </p>
                </div>
              </div>
              <button
                type="button"
                onClick={() => setGlobalApiError(null)}
                className="text-slate-400 hover:text-white text-xs px-2 py-1 rounded bg-slate-900 border border-slate-800 transition-colors"
              >
                Dismiss ✕
              </button>
            </div>

            <div className="bg-slate-950/80 rounded-xl p-3 border border-rose-900/40 font-mono text-[11px] space-y-1.5 text-rose-200">
              <div><strong className="text-slate-400">Target Endpoint:</strong> <span className="text-amber-300">{globalApiError.targetUrl}</span></div>
              <div><strong className="text-slate-400">Error Message:</strong> <span className="text-rose-400">{globalApiError.message}</span></div>
              {globalApiError.code && <div><strong className="text-slate-400">Error Code:</strong> <span>{globalApiError.code}</span></div>}
              {globalApiError.responseData && (
                <div className="mt-2 pt-2 border-t border-rose-900/30">
                  <strong className="text-slate-400 block mb-1">Server Response Data:</strong>
                  <pre className="text-[10px] text-slate-300 bg-slate-900 p-2 rounded max-h-32 overflow-auto whitespace-pre-wrap">{globalApiError.responseData}</pre>
                </div>
              )}
            </div>

            {globalApiError.explanation && (
              <div className="text-xs text-slate-300 bg-slate-900/90 rounded-xl p-3 border border-slate-800 font-sans leading-relaxed whitespace-pre-line">
                <span className="font-bold text-amber-400 block mb-1">💡 Diagnostic Troubleshooting:</span>
                {globalApiError.explanation}
              </div>
            )}
          </div>
        )}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
          
          {/* LEFT COLUMN: 1. Select Input Type  +  2. Add Product Resource (Module 2) */}
          <div className="lg:col-span-5 space-y-6">
            
            {/* BOX 1: Select Input Type (Module 1) */}
            <div className="bg-slate-900/90 rounded-2xl border border-slate-800 p-6 shadow-xl space-y-6">
              <div>
                <label className="block text-sm font-semibold text-white uppercase tracking-wider mb-3">
                  1. Select Input Type
                </label>
                <div className="grid grid-cols-2 gap-2 bg-slate-950 p-1.5 rounded-xl border border-slate-800">
                  {[
                    { id: 'CSV', label: 'CSV File', icon: FileSpreadsheet },
                    { id: 'PDF', label: 'PDF Document', icon: FileText }
                  ].map((tab) => {
                    const Icon = tab.icon;
                    return (
                      <button
                        key={tab.id}
                        type="button"
                        onClick={() => {
                          setM1Tab(tab.id);
                          setM1Error(null);
                          setM1File(null);
                          setM1DetectedHeaders([]);
                          setM1Response(null);
                          setM1RawResponse(null);
                        }}
                        className={`flex items-center justify-center space-x-2 py-2.5 px-3 rounded-lg text-xs font-semibold transition-all ${
                          m1Tab === tab.id
                            ? 'bg-indigo-600 text-white shadow-md shadow-indigo-600/30'
                            : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
                        }`}
                      >
                        <Icon className="w-4 h-4" />
                        <span>{tab.label}</span>
                      </button>
                    );
                  })}
                </div>
              </div>

              <form onSubmit={handleM1Submit} className="space-y-5">
                {m1Tab === 'CSV' && (
                  <div className="space-y-3">
                    <div className="border-2 border-dashed border-slate-700 hover:border-emerald-500/50 rounded-xl p-6 text-center bg-slate-950/50 relative cursor-pointer">
                      <input type="file" accept=".csv" onChange={handleCsvFileChange} className="absolute inset-0 opacity-0 cursor-pointer w-full h-full" />
                      <FileSpreadsheet className="w-10 h-10 text-emerald-400 mx-auto mb-2" />
                      <p className="text-sm font-medium text-slate-200">{m1File?.name || 'Click or Drag CSV file here'}</p>
                      <p className="text-xs text-slate-500 mt-1">Supports Unihack 6-column catalogue CSV or any custom product CSV dataset</p>
                    </div>

                    {m1DetectedHeaders.length > 0 && (
                      <div className="p-3 bg-slate-950 rounded-xl border border-slate-800 space-y-2">
                        <span className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider block">
                          Detected Headers ({m1DetectedHeaders.length} columns)
                        </span>
                        <div className="flex flex-wrap gap-1.5">
                          {m1DetectedHeaders.map((col, idx) => (
                            <span key={idx} className="px-2 py-0.5 rounded bg-slate-800 text-[11px] font-mono text-emerald-300 border border-slate-700">
                              {col}
                            </span>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                )}

                {m1Tab === 'PDF' && (
                  <div className="border-2 border-dashed border-slate-700 hover:border-indigo-500/50 rounded-xl p-6 text-center bg-slate-950/50 relative cursor-pointer">
                    <input type="file" accept=".pdf" onChange={(e) => { setM1File(e.target.files?.[0]); setM1Response(null); setM1RawResponse(null); }} className="absolute inset-0 opacity-0 cursor-pointer w-full h-full" />
                    <UploadCloud className="w-10 h-10 text-indigo-400 mx-auto mb-2" />
                    <p className="text-sm font-medium text-slate-200">{m1File?.name || 'Click or Drag PDF file here'}</p>
                  </div>
                )}

                {m1Error && (
                  <div className="p-3 bg-rose-500/10 border border-rose-500/30 rounded-xl text-rose-300 text-xs flex items-center space-x-2">
                    <AlertCircle className="w-4 h-4 text-rose-400 shrink-0" />
                    <span>{m1Error}</span>
                  </div>
                )}

                <button type="submit" disabled={m1Loading} className="w-full py-3.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white font-semibold text-sm shadow-lg flex items-center justify-center space-x-2 transition-all">
                  {m1Loading ? <RefreshCw className="w-4 h-4 animate-spin text-white" /> : <span>Upload Product Input</span>}
                </button>
              </form>

              {/* PRODUCT SELECTOR SECTION */}
              {module1Products.length > 0 && (
                <div className="pt-5 border-t border-slate-800 space-y-4">
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-semibold text-white uppercase tracking-wider flex items-center space-x-1.5">
                      <Tag className="w-4 h-4 text-indigo-400" />
                      <span>PRODUCT SELECTOR</span>
                    </span>
                    <button
                      type="button"
                      onClick={fetchModule1Products}
                      className="text-[11px] text-indigo-400 hover:text-indigo-300 flex items-center space-x-1 bg-indigo-500/10 px-2 py-1 rounded-md"
                    >
                      <RefreshCw className={`w-3 h-3 ${productsLoading ? 'animate-spin' : ''}`} />
                      <span>Refresh</span>
                    </button>
                  </div>

                  {/* Dropdown Selector */}
                  <div>
                    <label className="block text-[11px] font-semibold text-slate-400 uppercase tracking-wider mb-1.5">
                      Select Product
                    </label>
                    <select
                      value={selectedProductId || ''}
                      onChange={(e) => setSelectedProductId(e.target.value)}
                      className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3.5 py-2.5 text-xs text-slate-200 focus:border-indigo-500 focus:outline-none cursor-pointer"
                    >
                      {module1Products
                        .filter((p) => {
                          if (!productSearchTerm.trim()) return true;
                          const term = productSearchTerm.toLowerCase();
                          return (
                            (p.product_name && p.product_name.toLowerCase().includes(term)) ||
                            (p.part_number && p.part_number.toLowerCase().includes(term)) ||
                            (p.sku && p.sku.toLowerCase().includes(term)) ||
                            (p.manufacturer && p.manufacturer.toLowerCase().includes(term)) ||
                            (p.brand && p.brand.toLowerCase().includes(term)) ||
                            (p.row_number !== null && p.row_number !== undefined && String(p.row_number).includes(term)) ||
                            (p.product_id && p.product_id.toLowerCase().includes(term))
                          );
                        })
                        .map((p) => (
                          <option key={p.product_id} value={p.product_id}>
                            {p.row_number ? `Row ${p.row_number}: ` : ''}{p.product_name || p.part_number || p.product_id}
                          </option>
                        ))}
                    </select>
                  </div>

                  {/* Selected Product Details Card */}
                  {selectedProductLoading ? (
                    <div className="p-4 bg-slate-950/50 rounded-xl border border-slate-800 text-center text-slate-500 text-xs">
                      Loading product details...
                    </div>
                  ) : selectedProduct ? (
                    <div className="bg-slate-950/80 rounded-xl border border-slate-800 p-4 space-y-3">
                      <div className="flex items-center justify-between border-b border-slate-800 pb-2">
                        <span className="text-xs font-semibold text-slate-200">Selected Product</span>
                        <span className="px-2 py-0.5 rounded text-[10px] font-mono bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                          {selectedProduct.status || 'READY_FOR_RESOLUTION'}
                        </span>
                      </div>

                      <div className="space-y-1.5 text-xs text-slate-300">
                        <div>
                          <strong className="text-slate-200">Product Name: </strong>
                          <span>{formatValue(selectedProduct.identity?.product_name)}</span>
                        </div>
                        <div>
                          <strong className="text-slate-200">Part Number: </strong>
                          <span className="font-mono text-indigo-300">{formatValue(selectedProduct.identity?.part_number)}</span>
                        </div>
                        <div>
                          <strong className="text-slate-200">SKU: </strong>
                          <span className="font-mono">{formatValue(selectedProduct.identity?.sku)}</span>
                        </div>
                        <div>
                          <strong className="text-slate-200">Manufacturer: </strong>
                          <span>{formatValue(selectedProduct.identity?.manufacturer)}</span>
                        </div>
                        <div>
                          <strong className="text-slate-200">Brand: </strong>
                          <span>{formatValue(selectedProduct.identity?.brand)}</span>
                        </div>
                        <div>
                          <strong className="text-slate-200">Model: </strong>
                          <span>{formatValue(selectedProduct.identity?.model)}</span>
                        </div>
                        <div>
                          <strong className="text-slate-200">Source Row: </strong>
                          <span className="font-mono">{formatValue(selectedProduct.source_record?.row_number || selectedProduct.metadata?.row_number)}</span>
                        </div>
                      </div>

                      {processSelectedSuccess && (
                        <div className="p-2.5 bg-emerald-500/10 border border-emerald-500/20 rounded-lg text-emerald-400 text-[11px] text-center font-medium">
                          {processSelectedSuccess}
                        </div>
                      )}

                      {/* Module 5 Trigger Button */}
                      <button
                        type="button"
                        onClick={handleRunModule5}
                        disabled={m5Loading}
                        className="w-full py-3 rounded-xl bg-gradient-to-r from-violet-600 to-indigo-600 hover:from-violet-500 hover:to-indigo-500 text-white font-semibold text-xs shadow-lg shadow-violet-600/20 flex items-center justify-center space-x-2 transition-all active:scale-[0.98]"
                      >
                        {m5Loading ? (
                          <><RefreshCw className="w-3.5 h-3.5 animate-spin" /><span>Interpreting…</span></>
                        ) : (
                          <><Sparkles className="w-3.5 h-3.5" /><span>Extract & Structure Data</span></>
                        )}
                      </button>

                      {m5Error && (
                        <div className="p-2.5 bg-rose-500/10 border border-rose-500/20 rounded-lg text-rose-400 text-[11px] flex items-start space-x-2">
                          <AlertCircle className="w-3.5 h-3.5 shrink-0 mt-0.5" />
                          <span>{m5Error}</span>
                        </div>
                      )}
                    </div>
                  ) : null}
                </div>
              )}
            </div>

            {/* BOX 2: Add Product Resource (Module 2) BELOW Select Input Type */}
            <div className="bg-slate-900/90 rounded-2xl border border-slate-800 p-6 shadow-xl space-y-5">
              <div className="flex items-center justify-between border-b border-slate-800 pb-3">
                <h3 className="text-sm font-semibold text-slate-200 flex items-center space-x-2">
                  <Plus className="w-4 h-4 text-indigo-400" />
                  <span>2. Add Product Resource (Module 2)</span>
                </h3>
              </div>

              {/* Resource Type Selector Tabs */}
              <div className="grid grid-cols-3 gap-2 bg-slate-950 p-1.5 rounded-xl border border-slate-800">
                {[
                  { id: 'PDF', label: 'PDF File', icon: FileText },
                  { id: 'URL', label: 'Web URL', icon: Globe },
                  { id: 'TEXT', label: 'Raw Text', icon: FileCode }
                ].map((tab) => {
                  const Icon = tab.icon;
                  return (
                    <button
                      key={tab.id}
                      type="button"
                      onClick={() => {
                        setResTab(tab.id);
                        setResError(null);
                      }}
                      className={`flex items-center justify-center space-x-1.5 py-2 px-2.5 rounded-lg text-xs font-semibold transition-all ${
                        resTab === tab.id
                          ? 'bg-indigo-600 text-white shadow-md shadow-indigo-600/30'
                          : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
                      }`}
                    >
                      <Icon className="w-3.5 h-3.5" />
                      <span>{tab.label}</span>
                    </button>
                  );
                })}
              </div>

              <form onSubmit={handleAddResource} className="space-y-4">
                {/* Resource Name */}
                <div>
                  <label className="block text-[11px] font-semibold text-slate-400 uppercase tracking-wider mb-1.5">
                    Resource Title / Name (Optional)
                  </label>
                  <input
                    type="text"
                    value={resName}
                    onChange={(e) => setResName(e.target.value)}
                    placeholder="e.g. ABB ACS880 Technical Datasheet"
                    className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3.5 py-2.5 text-xs text-slate-200 focus:border-indigo-500 focus:outline-none"
                  />
                </div>

                {/* PDF Intake */}
                {resTab === 'PDF' && (
                  <div className={`border-2 border-dashed ${resFile ? 'border-emerald-500/50 bg-emerald-950/20' : 'border-slate-700 hover:border-indigo-500/50 bg-slate-950/50'} rounded-xl p-5 text-center relative cursor-pointer transition-all`}>
                    <input
                      type="file"
                      accept=".pdf"
                      onChange={(e) => setResFile(e.target.files?.[0] || null)}
                      className="absolute inset-0 opacity-0 cursor-pointer w-full h-full"
                    />
                    <UploadCloud className={`w-8 h-8 ${resFile ? 'text-emerald-400' : 'text-indigo-400'} mx-auto mb-2`} />
                    {resFile ? (
                      <div>
                        <p className="text-xs font-semibold text-emerald-300">{resFile.name}</p>
                        <p className="text-[11px] text-slate-400 mt-0.5">{(resFile.size / 1024).toFixed(1)} KB • Ready to upload</p>
                      </div>
                    ) : (
                      <div>
                        <p className="text-xs font-medium text-slate-200">Select or Drag PDF document</p>
                        <p className="text-[10px] text-slate-500 mt-1">Computes SHA-256 & stores locally under storage/resources/</p>
                      </div>
                    )}
                  </div>
                )}

                {/* URL Intake */}
                {resTab === 'URL' && (
                  <div>
                    <label className="block text-[11px] font-semibold text-slate-400 uppercase tracking-wider mb-1.5">
                      Target Webpage URL
                    </label>
                    <input
                      type="url"
                      value={resUrl}
                      onChange={(e) => setResUrl(e.target.value)}
                      placeholder="https://example.com/product-specs"
                      className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3.5 py-2.5 text-xs text-slate-200 font-mono focus:border-indigo-500 focus:outline-none"
                    />
                  </div>
                )}

                {/* Text Intake */}
                {resTab === 'TEXT' && (
                  <div>
                    <label className="block text-[11px] font-semibold text-slate-400 uppercase tracking-wider mb-1.5">
                      Raw Technical Specifications / Notes
                    </label>
                    <textarea
                      rows={4}
                      value={resText}
                      onChange={(e) => setResText(e.target.value)}
                      placeholder="Paste technical specs, notes, or markdown content here..."
                      className="w-full bg-slate-950 border border-slate-800 rounded-xl p-3 text-xs text-slate-200 font-mono focus:border-indigo-500 focus:outline-none"
                    />
                  </div>
                )}

                {resError && (
                  <div className="p-3 bg-rose-500/10 border border-rose-500/30 rounded-xl text-rose-300 text-xs flex items-center space-x-2">
                    <AlertCircle className="w-4 h-4 text-rose-400 shrink-0" />
                    <span>{resError}</span>
                  </div>
                )}

                <button
                  type="submit"
                  disabled={resLoading}
                  className="w-full py-3 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white font-semibold text-xs shadow-lg flex items-center justify-center space-x-2 transition-all"
                >
                  {resLoading ? (
                    <RefreshCw className="w-4 h-4 animate-spin text-white" />
                  ) : (
                    <>
                      <Plus className="w-4 h-4" />
                      <span>Register & Collect Resource</span>
                    </>
                  )}
                </button>
              </form>
            </div>

          </div>

          {/* RIGHT COLUMN: Results Dashboard + Registered Resources Cards */}
          <div className="lg:col-span-7 space-y-6">
            
            {/* REGISTERED RESOURCES LIST (Module 2) */}
            <div className="bg-slate-900/90 rounded-2xl border border-slate-800 p-6 shadow-xl space-y-4">
              <div className="flex items-center justify-between border-b border-slate-800 pb-3">
                <div className="flex items-center space-x-2">
                  <Database className="w-4 h-4 text-indigo-400" />
                  <h3 className="text-sm font-semibold text-slate-200">
                    Registered Product Resources ({resources.length})
                  </h3>
                </div>
                <button
                  type="button"
                  onClick={() => fetchResources(activeRequestId)}
                  className="text-xs text-indigo-400 hover:text-indigo-300 flex items-center space-x-1"
                >
                  <RefreshCw className="w-3 h-3" />
                  <span>Refresh</span>
                </button>
              </div>

              {resources.length === 0 ? (
                <div className="p-6 text-center text-slate-500 border border-dashed border-slate-800 rounded-xl space-y-2">
                  <Box className="w-8 h-8 text-slate-700 mx-auto" />
                  <p className="text-xs">No resources registered for request <code className="text-indigo-300">{activeRequestId}</code>.</p>
                  <p className="text-[11px] text-slate-600">Use the "Add Product Resource" panel on the left to add PDF, URL, or Text resources.</p>
                </div>
              ) : (
                <div className="space-y-3 max-h-[300px] overflow-y-auto pr-1">
                  {resources.map((res) => {
                    const isProcessed = res.status === 'processed';
                    const isFailed = res.status === 'failed';
                    const isDuplicate = res.status === 'duplicate';

                    return (
                      <div
                        key={res.source_id}
                        className="bg-slate-950/80 rounded-xl border border-slate-800 p-3.5 hover:border-slate-700 transition-all flex flex-col md:flex-row md:items-center justify-between gap-3"
                      >
                        <div className="flex items-start space-x-3">
                          <div className="w-8 h-8 rounded-lg bg-slate-900 border border-slate-800 flex items-center justify-center text-indigo-400 shrink-0 mt-0.5">
                            {res.source_type === 'pdf' ? (
                              <FileText className="w-4 h-4" />
                            ) : res.source_type === 'url' ? (
                              <Globe className="w-4 h-4" />
                            ) : (
                              <FileCode className="w-4 h-4" />
                            )}
                          </div>

                          <div className="space-y-1">
                            <div className="flex items-center space-x-2">
                              <h4 className="text-xs font-bold text-slate-100">{res.source_name}</h4>
                              <span className="px-2 py-0.5 rounded text-[10px] font-mono bg-slate-900 text-indigo-300 border border-slate-800">
                                {res.source_id}
                              </span>
                            </div>

                            <div className="flex flex-wrap items-center gap-2 text-[11px] text-slate-400">
                              <span className="uppercase font-semibold text-slate-500">{res.source_type}</span>
                              {res.metadata?.page_count && (
                                <span>&bull; {res.metadata.page_count} pages</span>
                              )}
                              {res.metadata?.size_bytes && (
                                <span>&bull; {(res.metadata.size_bytes / 1024).toFixed(1)} KB</span>
                              )}
                              {res.metadata?.content_hash && (
                                <span className="font-mono text-[10px] text-slate-500">
                                  &bull; SHA: {res.metadata.content_hash.substring(0, 8)}...
                                </span>
                              )}
                            </div>
                          </div>
                        </div>

                        {/* Status Pill & Action Buttons */}
                        <div className="flex items-center space-x-2 self-end md:self-center">
                          {isProcessed && (
                            <span className="inline-flex items-center px-2.5 py-1 rounded-full text-[10px] font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                              <CheckSquare className="w-3 h-3 mr-1" />
                              Ready
                            </span>
                          )}
                          {isDuplicate && (
                            <span className="inline-flex items-center px-2.5 py-1 rounded-full text-[10px] font-semibold bg-amber-500/10 text-amber-400 border border-amber-500/20">
                              Already added
                            </span>
                          )}
                          {isFailed && (
                            <span className="inline-flex items-center px-2.5 py-1 rounded-full text-[10px] font-semibold bg-rose-500/10 text-rose-400 border border-rose-500/20">
                              Failed
                            </span>
                          )}

                          <button
                            type="button"
                            onClick={() => setSelectedResource(res)}
                            className="p-1.5 rounded-lg bg-slate-900 hover:bg-slate-800 text-slate-400 hover:text-slate-200 border border-slate-800"
                            title="View Details"
                          >
                            <Info className="w-3.5 h-3.5" />
                          </button>

                          <button
                            type="button"
                            onClick={() => handleDeleteResource(res.source_id)}
                            className="p-1.5 rounded-lg bg-rose-500/10 hover:bg-rose-500/20 text-rose-400 border border-rose-500/20"
                            title="Delete Resource"
                          >
                            <Trash2 className="w-3.5 h-3.5" />
                          </button>
                        </div>
                      </div>
                    );
                  })}
                </div>
              )}
            </div>



            {m1Response && (
              <div className="space-y-6">
                <div className="bg-gradient-to-r from-slate-900 via-indigo-950/30 to-slate-900 rounded-2xl border border-slate-800 p-5 shadow-xl space-y-4">
                  <div className="flex flex-wrap items-center justify-between gap-3">
                    <div className="flex items-center space-x-2">
                      <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                        <CheckCircle2 className="w-3.5 h-3.5 mr-1" />
                        Structured Output
                      </span>
                    </div>

                    <div className="flex items-center space-x-2">
                      <button
                        type="button"
                        onClick={handleDownloadCsv}
                        className="inline-flex items-center space-x-2 text-xs px-3 py-1.5 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white font-semibold shadow-md shadow-emerald-600/20 active:scale-[0.98] transition-all"
                      >
                        <Download className="w-3.5 h-3.5" />
                        <span>Download Output CSV</span>
                      </button>

                      <div className="flex bg-slate-950 p-1 rounded-lg border border-slate-800 text-xs">
                        <button
                          type="button"
                          onClick={() => setViewMode('SUMMARY')}
                          className={`px-3 py-1 rounded-md font-semibold transition-all ${
                            viewMode === 'SUMMARY' ? 'bg-indigo-600 text-white' : 'text-slate-400 hover:text-slate-200'
                          }`}
                        >
                          Form View
                        </button>
                        <button
                          type="button"
                          onClick={() => setViewMode('JSON')}
                          className={`px-3 py-1 rounded-md font-semibold transition-all ${
                            viewMode === 'JSON' ? 'bg-indigo-600 text-white' : 'text-slate-400 hover:text-slate-200'
                          }`}
                        >
                          JSON View
                        </button>
                      </div>
                    </div>
                  </div>
                </div>


                {viewMode === 'JSON' && (
                  <div className="bg-slate-900/90 rounded-2xl border border-slate-800 p-5 shadow-xl space-y-3">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-2">
                        <Code className="w-4 h-4 text-indigo-400" />
                        <h4 className="text-xs font-semibold text-slate-300 uppercase tracking-wider">
                          Full Standardized JSON Schema
                        </h4>
                      </div>
                      <button
                        type="button"
                        onClick={() => {
                          navigator.clipboard.writeText(JSON.stringify(m1RawResponse, null, 2));
                          setM1Copied(true);
                          setTimeout(() => setM1Copied(false), 2000);
                        }}
                        className="inline-flex items-center space-x-1 text-xs px-2.5 py-1 rounded-md bg-slate-800 hover:bg-slate-700 text-slate-300 border border-slate-700 transition-colors"
                      >
                        {m1Copied ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5 text-slate-400" />}
                        <span>{m1Copied ? 'Copied' : 'Copy JSON'}</span>
                      </button>
                    </div>

                    <div className="bg-slate-950 rounded-xl p-4 border border-slate-800 max-h-[450px] overflow-auto">
                      <pre className="text-xs font-mono text-indigo-200 leading-relaxed whitespace-pre-wrap">
                        {JSON.stringify(m1RawResponse, null, 2)}
                      </pre>
                    </div>
                  </div>
                )}
              </div>
            )}

            {/* MODULE 5 SEMANTIC INTERPRETATION RESULTS */}
            {m5Result && (
              <div className="bg-slate-900/90 rounded-2xl border border-violet-500/30 p-6 shadow-xl space-y-5">
                {/* Header */}
                <div className="flex items-center justify-between border-b border-slate-800 pb-3">
                  <div className="flex items-center space-x-2">
                    <div className="w-8 h-8 rounded-lg bg-gradient-to-tr from-violet-600 to-indigo-500 flex items-center justify-center shadow-lg shadow-violet-500/20">
                      <Sparkles className="w-4 h-4 text-white" />
                    </div>
                    <div>
                      <h3 className="text-sm font-bold text-white">Structured Extraction</h3>
                      <p className="text-[11px] text-slate-400">Candidate Product Data Extraction</p>
                    </div>
                  </div>
                  <span className="inline-flex items-center px-2.5 py-1 rounded-full text-[10px] font-semibold bg-amber-500/10 text-amber-400 border border-amber-500/20">
                    CANDIDATE
                  </span>
                </div>

                {/* Stats Row */}
                <div className="grid grid-cols-3 gap-3">
                  <div className="bg-slate-950 rounded-xl border border-slate-800 p-3 text-center">
                    <span className="text-lg font-bold text-violet-400">{m5Result.populated_fields_count}</span>
                    <p className="text-[10px] text-slate-500 mt-0.5">Fields Populated</p>
                  </div>
                  <div className="bg-slate-950 rounded-xl border border-slate-800 p-3 text-center">
                    <span className="text-lg font-bold text-indigo-400">{m5Result.inferred_fields_count}</span>
                    <p className="text-[10px] text-slate-500 mt-0.5">LLM Inferred</p>
                  </div>
                  <div className="bg-slate-950 rounded-xl border border-slate-800 p-3 text-center">
                    <span className="text-lg font-bold text-emerald-400">{m5Result.processing_time_ms?.toFixed(0)}ms</span>
                    <p className="text-[10px] text-slate-500 mt-0.5">Processing Time</p>
                  </div>
                </div>


                {/* Semantic Metadata — per-field provenance */}
                {m5Result.semantic_metadata && m5Result.semantic_metadata.length > 0 && (
                  <div className="space-y-2">
                    <h4 className="text-xs font-semibold text-slate-400 uppercase tracking-wider flex items-center space-x-1.5">
                      <Database className="w-3.5 h-3.5 text-indigo-400" />
                      <span>Field Provenance ({m5Result.semantic_metadata.length} fields)</span>
                    </h4>
                    <div className="max-h-52 overflow-y-auto space-y-1.5 pr-1">
                      {m5Result.semantic_metadata.map((meta, idx) => (
                        <div key={idx} className="bg-slate-950 rounded-lg border border-slate-800 px-3 py-2 flex flex-wrap items-center gap-2 text-[11px]">
                          <span className="font-mono font-bold text-indigo-300 shrink-0">{meta.field}</span>
                          <span className="text-slate-400 flex-1 truncate">{meta.value || '—'}</span>
                          <span className={`px-1.5 py-0.5 rounded text-[10px] font-semibold border shrink-0 ${
                            meta.source === 'SOURCE_EVIDENCE' ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20' :
                            meta.source === 'ORG_CONTEXT' ? 'bg-blue-500/10 text-blue-400 border-blue-500/20' :
                            'bg-violet-500/10 text-violet-400 border-violet-500/20'
                          }`}>{meta.source}</span>
                          <span className="text-slate-600 shrink-0">{((meta.llm_confidence || 0) * 100).toFixed(0)}%</span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* 252-Column Candidate Preview */}
                <div className="border border-slate-800 rounded-xl overflow-hidden">
                  <button
                    type="button"
                    onClick={() => setM5Show252(!m5Show252)}
                    className="w-full flex items-center justify-between px-4 py-3 bg-slate-950 text-xs font-semibold text-slate-300 hover:text-white transition-colors"
                  >
                    <span className="flex items-center space-x-2">
                      <Code className="w-3.5 h-3.5 text-violet-400" />
                      <span>252-Column Candidate Delivery Record</span>
                    </span>
                    <span className="text-slate-500">{m5Show252 ? '▲ Collapse' : '▼ Expand'}</span>
                  </button>
                  {m5Show252 && (
                    <div className="bg-slate-950/50 border-t border-slate-800 p-4 max-h-96 overflow-auto">
                      <table className="w-full text-[11px] font-mono border-collapse">
                        <thead>
                          <tr>
                            <th className="text-left text-slate-500 font-semibold pb-2 pr-4 w-48">Field</th>
                            <th className="text-left text-slate-500 font-semibold pb-2">Value</th>
                          </tr>
                        </thead>
                        <tbody>
                          {Object.entries(m5Result.delivery_record || {}).map(([key, val]) => (
                            <tr key={key} className={`border-t border-slate-800/50 ${val ? '' : 'opacity-40'}`}>
                              <td className="py-1 pr-4 text-indigo-300 align-top whitespace-nowrap">{key}</td>
                              <td className="py-1 text-slate-300 break-all">{val || <span className="text-slate-600 italic">—</span>}</td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  )}
                </div>
              </div>
            )}

            {/* STRUCTURED OUTPUT RESULT (Module 1) */}
            {!m1Response && !m1Loading && !m5Result && (
              <div className="bg-slate-900/60 rounded-2xl border border-slate-800/80 p-12 text-center text-slate-500 space-y-3">
                <Box className="w-12 h-12 text-slate-700 mx-auto" />
                <h3 className="text-sm font-semibold text-slate-400">Structured Output</h3>
                <p className="text-xs text-slate-500 max-w-sm mx-auto">
                  Upload a CSV dataset or PDF document to extract candidate product identities and view generated StandardProductInput objects.
                </p>
              </div>
            )}

          </div>

        </div>

        {/* Resource Details Modal Drawer */}
        {selectedResource && (
          <div className="fixed inset-0 bg-slate-950/80 backdrop-blur-sm z-50 flex items-center justify-center p-4">
            <div className="bg-slate-900 border border-slate-800 rounded-2xl max-w-lg w-full p-6 shadow-2xl space-y-4">
              <div className="flex items-center justify-between border-b border-slate-800 pb-3">
                <h3 className="text-sm font-bold text-white flex items-center space-x-2">
                  <Info className="w-4 h-4 text-indigo-400" />
                  <span>Resource Details & Metadata</span>
                </h3>
                <button
                  onClick={() => setSelectedResource(null)}
                  className="text-slate-400 hover:text-slate-200 text-xs font-semibold"
                >
                  Close ✕
                </button>
              </div>

              <div className="space-y-2 text-xs font-mono">
                <div className="bg-slate-950 p-3 rounded-xl border border-slate-800 flex justify-between">
                  <span className="text-slate-500">Source ID:</span>
                  <span className="text-indigo-300 font-bold">{selectedResource.source_id}</span>
                </div>
                <div className="bg-slate-950 p-3 rounded-xl border border-slate-800 flex justify-between">
                  <span className="text-slate-500">Name:</span>
                  <span className="text-slate-200">{selectedResource.source_name}</span>
                </div>
                <div className="bg-slate-950 p-3 rounded-xl border border-slate-800 flex justify-between">
                  <span className="text-slate-500">Type / Subtype:</span>
                  <span className="text-slate-200">{selectedResource.source_type} / {selectedResource.source_subtype}</span>
                </div>
                <div className="bg-slate-950 p-3 rounded-xl border border-slate-800 flex justify-between">
                  <span className="text-slate-500">Status:</span>
                  <span className="text-emerald-400 font-bold">{selectedResource.status}</span>
                </div>
                {selectedResource.error_message && (
                  <div className="bg-rose-500/10 p-3 rounded-xl border border-rose-500/30 text-rose-300">
                    <span className="font-semibold block mb-1">Error Message:</span>
                    {selectedResource.error_message}
                  </div>
                )}
                {selectedResource.metadata?.content_hash && (
                  <div className="bg-slate-950 p-3 rounded-xl border border-slate-800 space-y-1">
                    <span className="text-slate-500 block">SHA-256 Content Hash:</span>
                    <span className="text-indigo-300 text-[10px] break-all">{selectedResource.metadata.content_hash}</span>
                  </div>
                )}
              </div>
            </div>
          </div>
        )}

      </main>

      {/* Footer */}
      <footer className="border-t border-slate-900 bg-slate-950 py-4 px-6 text-center text-xs text-slate-600">
        ProductDNA Intelligence Platform &bull; Product Intake & Resource Collection Engine
      </footer>
    </div>
  );
}
