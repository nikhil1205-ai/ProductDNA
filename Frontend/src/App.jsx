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
  RefreshCw,
  Layers,
  Database,
  Plus,
  Trash2,
  FileCode,
  ShieldCheck,
  Search,
  ExternalLink,
  ChevronRight
} from 'lucide-react';

const MODULE1_API_URL = 'http://localhost:8000/api/product-input';
const MODULE4_API_URL = 'http://localhost:8000/api/evidence/extract';

export default function App() {
  // Top-level Navigation: 'MODULE1' or 'MODULE4'
  const [activeModule, setActiveModule] = useState('MODULE1');

  // --- MODULE 1 STATE ---
  const [m1Tab, setM1Tab] = useState('CSV');
  const [m1File, setM1File] = useState(null);
  const [m1ProductName, setM1ProductName] = useState('');
  const [m1Url, setM1Url] = useState('');
  const [m1JsonText, setM1JsonText] = useState('');
  const [m1Loading, setM1Loading] = useState(false);
  const [m1Response, setM1Response] = useState(null);
  const [m1SelectedRowIndex, setM1SelectedRowIndex] = useState(0);
  const [m1DetectedHeaders, setM1DetectedHeaders] = useState([]);
  const [m1Error, setM1Error] = useState(null);
  const [m1Copied, setM1Copied] = useState(false);

  const handleCsvFileChange = (e) => {
    const file = e.target.files?.[0];
    setM1File(file || null);
    setM1Response(null);
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

  // --- MODULE 4 STATE ---
  const [m4ProductName, setM4ProductName] = useState('ABB ACS880 Industrial Drive');
  const [m4Brand, setM4Brand] = useState('ABB');
  const [m4Manufacturer, setM4Manufacturer] = useState('ABB');
  const [m4Model, setM4Model] = useState('ACS880-01-145A-3');
  const [m4Sku, setM4Sku] = useState('ACS880-01-145A-3');
  const [m4Category, setM4Category] = useState('Industrial Drives');
  const [m4ResolutionStatus, setM4ResolutionStatus] = useState('AMBIGUOUS');

  // User-provided sources array for Module 4
  const [m4Sources, setM4Sources] = useState([
    {
      id: 'src-1',
      type: 'pdf',
      name: 'ACS880 Datasheet',
      value: 'acs880_datasheet.pdf',
      file: null,
      presetText: 'Input voltage: 380-480 V\nRated power: 75 kW\nRated current: 145 A\nMains frequency: 50/60 Hz\nProtection class: IP21\nApplications: Designed for pumps, fans and conveyors.'
    },
    {
      id: 'src-2',
      type: 'text',
      name: 'Technical Notes',
      value: 'Technical Notes: Operating temperature -15°C to 50°C. Wall-mounted drive.',
      file: null
    }
  ]);

  // Form input state for adding a new source
  const [newSrcType, setNewSrcType] = useState('url');
  const [newSrcName, setNewSrcName] = useState('');
  const [newSrcValue, setNewSrcValue] = useState('');
  const [newSrcFile, setNewSrcFile] = useState(null);

  const [m4Loading, setM4Loading] = useState(false);
  const [m4Response, setM4Response] = useState(null);
  const [m4Error, setM4Error] = useState(null);
  const [m4Copied, setM4Copied] = useState(false);
  const [selectedInputFile, setSelectedInputFile] = useState('REQ-20260816-2AD355E9.json');

  const handleExtractFromFile = async () => {
    setM4Loading(true);
    setM4Error(null);
    setM4Response(null);
    try {
      const res = await axios.get(`http://localhost:8000/api/evidence/extract-file?filename=${selectedInputFile}`);
      if (res && res.data) {
        setM4Response(res.data);
        const identity = res.data.product_identity || {};
        setM4ProductName(identity.product_name || '');
        setM4Brand(identity.brand || '');
        setM4Manufacturer(identity.manufacturer || '');
        setM4Model(identity.model || '');
        setM4Sku(identity.sku || '');
        setM4Category(identity.category || '');
        if (res.data.sources) {
          setM4Sources(res.data.sources.map(s => ({
            id: s.source_id,
            type: s.source_type,
            name: s.source_name,
            value: s.metadata?.url || s.metadata?.filename || 'dummy_source.txt',
            file: null
          })));
        }
      }
    } catch (err) {
      if (err.response?.data?.detail) setM4Error(err.response.data.detail);
      else setM4Error(err.message || 'Failed to process file.');
    } finally {
      setM4Loading(false);
    }
  };


  // Module 1 Handlers
  const handleM1Submit = async (e) => {
    e.preventDefault();
    setM1Loading(true);
    setM1Error(null);
    setM1Response(null);

    try {
      let res;
      if (m1Tab === 'PDF' || m1Tab === 'CSV') {
        const expectedExt = m1Tab.toLowerCase();
        if (!m1File || !m1File.name.toLowerCase().endsWith('.' + expectedExt)) {
          throw new Error(`Please select or upload a valid .${expectedExt} file.`);
        }
        const formData = new FormData();
        formData.append('file', m1File);
        formData.append('input_type', m1Tab);
        res = await axios.post(MODULE1_API_URL, formData, {
          headers: { 'Content-Type': 'multipart/form-data' }
        });
      } else if (m1Tab === 'PRODUCT_NAME') {
        if (!m1ProductName.trim()) throw new Error('Please enter a product name or text details.');
        const formData = new FormData();
        formData.append('input_text', m1ProductName);
        formData.append('input_type', 'PRODUCT_NAME');
        res = await axios.post(MODULE1_API_URL, formData);
      } else if (m1Tab === 'URL') {
        if (!m1Url.trim()) throw new Error('Please enter a target URL.');
        const formData = new FormData();
        formData.append('url', m1Url);
        formData.append('input_type', 'URL');
        res = await axios.post(MODULE1_API_URL, formData);
      } else if (m1Tab === 'JSON') {
        if (!m1JsonText.trim()) throw new Error('Please enter JSON payload text.');
        let parsed;
        try { parsed = JSON.parse(m1JsonText); }
        catch (err) { throw new Error('Invalid JSON string syntax.'); }
        res = await axios.post(MODULE1_API_URL, { input_type: 'JSON', json_data: parsed });
      }

      if (res && res.data) {
        if (res.data.status === 'ERROR') setM1Error(res.data.error || 'Processing error.');
        else setM1Response(res.data);
      }
    } catch (err) {
      if (err.response?.data?.error) setM1Error(err.response.data.error);
      else setM1Error(err.message || 'Failed to connect to backend.');
    } finally {
      setM1Loading(false);
    }
  };

  // Load Preset for Module 4 ABB ACS880 Drive
  const loadM4AbbPreset = () => {
    setM4ProductName('ABB ACS880 Industrial Drive');
    setM4Brand('ABB');
    setM4Manufacturer('ABB');
    setM4Model('ACS880-01-145A-3');
    setM4Sku('ACS880-01-145A-3');
    setM4Category('Industrial Drives');
    setM4ResolutionStatus('AMBIGUOUS');
    setM4Sources([
      {
        id: 'src-1',
        type: 'pdf',
        name: 'ACS880 Datasheet',
        value: 'acs880_datasheet.pdf',
        file: null,
        presetText: 'Input voltage: 380-480 V\nRated power: 75 kW\nRated current: 145 A\nMains frequency: 50/60 Hz\nProtection class: IP21\nApplications: Designed for pumps, fans and conveyors.'
      },
      {
        id: 'src-2',
        type: 'text',
        name: 'Technical Notes',
        value: 'Technical Notes: Operating temperature -15°C to 50°C. Wall-mounted drive.',
        file: null
      }
    ]);
  };

  // Load Preset for Module 4 SKF Ball Bearing
  const loadM4SkfPreset = () => {
    setM4ProductName('SKF 6205 Deep Groove Ball Bearing');
    setM4Brand('SKF');
    setM4Manufacturer('SKF Group');
    setM4Model('6205-2RSH');
    setM4Sku('6205');
    setM4Category('Bearings');
    setM4ResolutionStatus('MATCHED');
    setM4Sources([
      {
        id: 'src-skf-1',
        type: 'text',
        name: 'SKF 6205 Specifications',
        value: '# Technical Specifications\nBore diameter: 25 mm\nOuter diameter: 52 mm\nWidth: 15 mm\nDynamic load rating: 14.8 kN\nLimiting speed: 14000 rpm\nWeight: 0.13 kg',
        file: null
      }
    ]);
  };

  // Add source to Module 4 list
  const handleAddSource = (e) => {
    e.preventDefault();
    if (newSrcType === 'url' && !newSrcValue.trim()) return;
    if (newSrcType === 'text' && !newSrcValue.trim()) return;
    if (newSrcType === 'pdf' && !newSrcFile && !newSrcValue.trim()) return;

    const newSrc = {
      id: `src-${Date.now()}`,
      type: newSrcType,
      name: newSrcName || (newSrcFile ? newSrcFile.name : newSrcValue.slice(0, 30)),
      value: newSrcFile ? newSrcFile.name : newSrcValue,
      file: newSrcFile
    };

    setM4Sources([...m4Sources, newSrc]);
    setNewSrcName('');
    setNewSrcValue('');
    setNewSrcFile(null);
  };

  // Remove source from Module 4 list
  const handleRemoveSource = (id) => {
    setM4Sources(m4Sources.filter(s => s.id !== id));
  };

  // Module 4 Submit Handler
  const handleM4Submit = async (e) => {
    e.preventDefault();
    setM4Loading(true);
    setM4Error(null);
    setM4Response(null);

    try {
      // Build Module 4 Request JSON payload
      const sourcesPayload = m4Sources.map(s => ({
        type: s.type,
        value: s.presetText ? s.presetText : s.value,
        name: s.name,
        subtype: s.type === 'pdf' ? 'technical_datasheet' : s.type === 'url' ? 'website' : 'technical_notes'
      }));

      const payload = {
        request_id: `REQ-${Date.now().toString(16).toUpperCase()}`,
        identity: {
          product_name: m4ProductName,
          brand: m4Brand,
          manufacturer: m4Manufacturer,
          model: m4Model,
          sku: m4Sku,
          category: m4Category
        },
        status: m4ResolutionStatus,
        sources: sourcesPayload
      };

      const res = await axios.post(MODULE4_API_URL, payload);
      if (res && res.data) {
        if (res.data.status === 'FAILED') setM4Error(res.data.error || 'Evidence extraction failed.');
        else setM4Response(res.data);
      }
    } catch (err) {
      if (err.response?.data?.detail) setM4Error(err.response.data.detail);
      else if (err.response?.data?.error) setM4Error(err.response.data.error);
      else setM4Error(err.message || 'Failed to connect to backend server on http://localhost:8000.');
    } finally {
      setM4Loading(false);
    }
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
                ProductDNA Engine
              </h1>
              <p className="text-xs text-slate-400 font-medium">Industrial Product Intelligence Architecture</p>
            </div>
          </div>

          {/* Module Navigation Tabs */}
          <div className="flex items-center space-x-2 bg-slate-950 p-1 rounded-xl border border-slate-800">
            <button
              type="button"
              onClick={() => setActiveModule('MODULE1')}
              className={`flex items-center space-x-2 px-4 py-1.5 rounded-lg text-xs font-semibold transition-all ${
                activeModule === 'MODULE1'
                  ? 'bg-indigo-600 text-white shadow-md shadow-indigo-600/30'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
              }`}
            >
              <FileCode className="w-3.5 h-3.5" />
              <span>Module 1: Product Intake</span>
            </button>

            <button
              type="button"
              onClick={() => setActiveModule('MODULE4')}
              className={`flex items-center space-x-2 px-4 py-1.5 rounded-lg text-xs font-semibold transition-all ${
                activeModule === 'MODULE4'
                  ? 'bg-gradient-to-r from-indigo-600 to-violet-600 text-white shadow-md shadow-indigo-600/30'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
              }`}
            >
              <Layers className="w-3.5 h-3.5" />
              <span>Module 4: Evidence Extraction</span>
            </button>
          </div>

          <div className="flex items-center space-x-2">
            <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
              <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse mr-2"></span>
              Backend Ready (FastAPI :8000)
            </span>
          </div>
        </div>
      </header>

      {/* Main Content Area */}
      <main className="flex-1 max-w-7xl w-full mx-auto p-6 space-y-6">

        {/* MODULE 4 VIEW */}
        {activeModule === 'MODULE4' && (
          <div className="space-y-6">
            {/* Hero Section */}
            <section className="bg-gradient-to-r from-slate-900 via-indigo-950/40 to-slate-900 rounded-2xl p-6 border border-slate-800 shadow-xl relative overflow-hidden">
              <div className="absolute top-0 right-0 w-96 h-96 bg-indigo-500/10 rounded-full blur-3xl -mr-20 -mt-20 pointer-events-none"></div>
              <div className="relative z-10 space-y-2">
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-2">
                    <span className="px-2.5 py-0.5 rounded-full text-xs font-bold bg-indigo-500/20 text-indigo-300 border border-indigo-500/30">
                      Module 4 Engine
                    </span>
                    <h2 className="text-2xl font-bold text-white tracking-tight">
                      Evidence Collection & Structured Extraction Engine
                    </h2>
                  </div>

                  {/* Preset Loaders */}
                  <div className="flex items-center space-x-2">
                    <button
                      type="button"
                      onClick={loadM4AbbPreset}
                      className="inline-flex items-center text-xs text-indigo-300 hover:text-white bg-indigo-500/20 hover:bg-indigo-500/30 px-3 py-1.5 rounded-lg border border-indigo-500/30 transition-all font-medium"
                    >
                      <Sparkles className="w-3.5 h-3.5 mr-1 text-indigo-400" />
                      Load ABB ACS880 Drive
                    </button>
                    <button
                      type="button"
                      onClick={loadM4SkfPreset}
                      className="inline-flex items-center text-xs text-emerald-300 hover:text-white bg-emerald-500/20 hover:bg-emerald-500/30 px-3 py-1.5 rounded-lg border border-emerald-500/30 transition-all font-medium"
                    >
                      <Sparkles className="w-3.5 h-3.5 mr-1 text-emerald-400" />
                      Load SKF 6205 Bearing
                    </button>
                  </div>
                </div>

                <p className="text-xs text-slate-300 max-w-4xl leading-relaxed">
                  Accepts resolved product information from Module 2 (supporting <code className="text-indigo-300 font-mono">MATCHED</code>, <code className="text-amber-300 font-mono">AMBIGUOUS</code>, or <code className="text-rose-300 font-mono">NOT_FOUND</code>), ingests multi-sources (PDFs, Web URLs, Text documents), extracts canonical product attributes with full provenance (source ID, page, section, confidence), and validates schemas using Pydantic for Module 6.
                </p>
              </div>
            </section>

            {/* Grid Layout */}
            <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
              
              {/* Left Column: Module 2 Input & Source Intake */}
              <div className="lg:col-span-5 space-y-6">
                
                {/* Standard Input File Loader Box */}
                <div className="bg-slate-900/90 rounded-2xl border border-slate-800 p-5 shadow-xl space-y-4">
                  <div className="flex items-center space-x-2 pb-3 border-b border-slate-800">
                    <Database className="w-4 h-4 text-indigo-400" />
                    <h3 className="text-xs font-semibold text-slate-300 uppercase tracking-wider">
                      Standard Input (Module 2 Files)
                    </h3>
                  </div>
                  
                  <div className="flex items-center space-x-3 text-xs">
                    <select
                      value={selectedInputFile}
                      onChange={(e) => setSelectedInputFile(e.target.value)}
                      className="flex-1 bg-slate-950 border border-slate-800 rounded-lg p-2.5 text-xs text-slate-200 font-mono focus:border-indigo-500 focus:outline-none"
                    >
                      <option value="REQ-20260816-2AD355E9.json">REQ-20260816-2AD355E9.json</option>
                      <option value="REQ-20260816-605FDEE3.json">REQ-20260816-605FDEE3.json</option>
                      <option value="REQ-20260816-A560C0D9.json">REQ-20260816-A560C0D9.json</option>
                      <option value="REQ-20260816-BD19ABE4.json">REQ-20260816-BD19ABE4.json</option>
                      <option value="REQ-20260816-FE74ECA8.json">REQ-20260816-FE74ECA8.json</option>
                    </select>

                    <button
                      type="button"
                      onClick={handleExtractFromFile}
                      className="px-4 py-2.5 rounded-lg bg-indigo-600 hover:bg-indigo-500 font-semibold text-xs text-white shadow-md shadow-indigo-600/20 active:scale-[0.98] transition-all shrink-0"
                    >
                      Process File
                    </button>
                  </div>
                </div>

                {/* Product Identity Box */}
                <div className="bg-slate-900/90 rounded-2xl border border-slate-800 p-5 shadow-xl space-y-4">
                  <div className="flex items-center justify-between pb-3 border-b border-slate-800">
                    <div className="flex items-center space-x-2">
                      <Database className="w-4 h-4 text-indigo-400" />
                      <h3 className="text-xs font-semibold text-slate-300 uppercase tracking-wider">
                        1. Resolved Product Identity (Module 2 Input)
                      </h3>
                    </div>
                    <select
                      value={m4ResolutionStatus}
                      onChange={(e) => setM4ResolutionStatus(e.target.value)}
                      className="bg-slate-950 border border-slate-800 rounded-lg text-xs font-bold px-2.5 py-1 text-indigo-300 focus:outline-none"
                    >
                      <option value="AMBIGUOUS">AMBIGUOUS</option>
                      <option value="MATCHED">MATCHED</option>
                      <option value="NOT_FOUND">NOT_FOUND</option>
                    </select>
                  </div>

                  <div className="grid grid-cols-2 gap-3 text-xs">
                    <div>
                      <label className="block text-slate-500 mb-1">Product Name</label>
                      <input
                        type="text"
                        value={m4ProductName}
                        onChange={(e) => setM4ProductName(e.target.value)}
                        className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-slate-200 text-xs font-medium focus:border-indigo-500 focus:outline-none"
                      />
                    </div>
                    <div>
                      <label className="block text-slate-500 mb-1">Brand / Manufacturer</label>
                      <input
                        type="text"
                        value={m4Brand}
                        onChange={(e) => setM4Brand(e.target.value)}
                        className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-slate-200 text-xs font-medium focus:border-indigo-500 focus:outline-none"
                      />
                    </div>
                    <div>
                      <label className="block text-slate-500 mb-1">Model</label>
                      <input
                        type="text"
                        value={m4Model}
                        onChange={(e) => setM4Model(e.target.value)}
                        className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-slate-200 text-xs font-medium focus:border-indigo-500 focus:outline-none"
                      />
                    </div>
                    <div>
                      <label className="block text-slate-500 mb-1">SKU / Part Number</label>
                      <input
                        type="text"
                        value={m4Sku}
                        onChange={(e) => setM4Sku(e.target.value)}
                        className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-slate-200 text-xs font-medium focus:border-indigo-500 focus:outline-none"
                      />
                    </div>
                  </div>
                </div>

                {/* Sources Intake Box */}
                <div className="bg-slate-900/90 rounded-2xl border border-slate-800 p-5 shadow-xl space-y-4">
                  <div className="flex items-center justify-between pb-3 border-b border-slate-800">
                    <div className="flex items-center space-x-2">
                      <Layers className="w-4 h-4 text-indigo-400" />
                      <h3 className="text-xs font-semibold text-slate-300 uppercase tracking-wider">
                        2. Attached Product Sources ({m4Sources.length})
                      </h3>
                    </div>
                  </div>

                  {/* Sources List */}
                  <div className="space-y-2 max-h-[220px] overflow-auto pr-1">
                    {m4Sources.length === 0 ? (
                      <p className="text-xs text-slate-500 italic text-center py-4">No sources attached yet. Add a source below.</p>
                    ) : (
                      m4Sources.map((src) => (
                        <div key={src.id} className="flex items-center justify-between bg-slate-950 p-3 rounded-xl border border-slate-800 text-xs">
                          <div className="flex items-center space-x-2.5 truncate mr-2">
                            {src.type === 'pdf' && <FileText className="w-4 h-4 text-rose-400 shrink-0" />}
                            {src.type === 'url' && <LinkIcon className="w-4 h-4 text-indigo-400 shrink-0" />}
                            {src.type === 'text' && <FileSpreadsheet className="w-4 h-4 text-emerald-400 shrink-0" />}
                            <div className="truncate">
                              <span className="font-semibold text-slate-200 block truncate">{src.name}</span>
                              <span className="text-[10px] text-slate-500 block font-mono truncate">{src.value}</span>
                            </div>
                          </div>
                          <button
                            type="button"
                            onClick={() => handleRemoveSource(src.id)}
                            className="p-1 text-slate-500 hover:text-rose-400 transition-colors"
                            title="Remove source"
                          >
                            <Trash2 className="w-3.5 h-3.5" />
                          </button>
                        </div>
                      ))
                    )}
                  </div>

                  {/* Add New Source Form */}
                  <form onSubmit={handleAddSource} className="pt-3 border-t border-slate-800 space-y-3">
                    <label className="block text-[11px] font-semibold text-slate-400 uppercase tracking-wider">
                      Attach New Source
                    </label>
                    <div className="grid grid-cols-3 gap-2">
                      {['url', 'pdf', 'text'].map((stype) => (
                        <button
                          key={stype}
                          type="button"
                          onClick={() => setNewSrcType(stype)}
                          className={`py-1.5 rounded-lg text-xs font-semibold uppercase tracking-wider border transition-all ${
                            newSrcType === stype
                              ? 'bg-indigo-600 text-white border-indigo-500 shadow-md shadow-indigo-600/20'
                              : 'bg-slate-950 text-slate-400 border-slate-800 hover:bg-slate-800'
                          }`}
                        >
                          {stype}
                        </button>
                      ))}
                    </div>

                    <div className="space-y-2">
                      <input
                        type="text"
                        placeholder="Source Label e.g. Technical Datasheet"
                        value={newSrcName}
                        onChange={(e) => setNewSrcName(e.target.value)}
                        className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-xs text-slate-200 placeholder-slate-600 focus:outline-none focus:border-indigo-500"
                      />

                      {newSrcType === 'url' && (
                        <input
                          type="url"
                          placeholder="https://example.com/product-specs"
                          value={newSrcValue}
                          onChange={(e) => setNewSrcValue(e.target.value)}
                          className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-xs font-mono text-indigo-300 placeholder-slate-600 focus:outline-none focus:border-indigo-500"
                        />
                      )}

                      {newSrcType === 'text' && (
                        <textarea
                          rows={3}
                          placeholder="Paste technical text e.g. Input voltage: 380-480 V, Rated power: 75 kW"
                          value={newSrcValue}
                          onChange={(e) => setNewSrcValue(e.target.value)}
                          className="w-full bg-slate-950 border border-slate-800 rounded-lg p-2.5 text-xs text-slate-200 placeholder-slate-600 focus:outline-none focus:border-indigo-500 font-mono"
                        />
                      )}

                      {newSrcType === 'pdf' && (
                        <div className="border border-dashed border-slate-700 hover:border-indigo-500/50 rounded-lg p-3 text-center bg-slate-950/50 relative cursor-pointer">
                          <input
                            type="file"
                            accept=".pdf"
                            onChange={(e) => setNewSrcFile(e.target.files ? e.target.files[0] : null)}
                            className="absolute inset-0 opacity-0 cursor-pointer w-full h-full"
                          />
                          <p className="text-xs text-slate-300 font-medium">
                            {newSrcFile ? newSrcFile.name : 'Click to select local PDF file'}
                          </p>
                        </div>
                      )}

                      <button
                        type="submit"
                        className="w-full py-2 px-3 rounded-lg bg-slate-800 hover:bg-slate-700 text-xs font-semibold text-slate-200 flex items-center justify-center space-x-1.5 transition-colors border border-slate-700"
                      >
                        <Plus className="w-3.5 h-3.5 text-indigo-400" />
                        <span>Add Source to Queue</span>
                      </button>
                    </div>
                  </form>
                </div>

                {/* Error Banner */}
                {m4Error && (
                  <div className="p-4 bg-rose-500/10 border border-rose-500/30 rounded-xl flex items-start space-x-3 text-rose-300 text-xs">
                    <AlertCircle className="w-4 h-4 text-rose-400 mt-0.5 shrink-0" />
                    <div>
                      <strong className="font-semibold block text-rose-200">Extraction Error</strong>
                      <span>{m4Error}</span>
                    </div>
                  </div>
                )}

                {/* Main Action Button */}
                <button
                  type="button"
                  onClick={handleM4Submit}
                  disabled={m4Loading || m4Sources.length === 0}
                  className="w-full py-3.5 px-6 rounded-xl bg-gradient-to-r from-indigo-600 via-violet-600 to-indigo-600 hover:from-indigo-500 hover:to-violet-500 text-white font-semibold text-sm shadow-lg shadow-indigo-600/30 transition-all flex items-center justify-center space-x-2 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {m4Loading ? (
                    <>
                      <RefreshCw className="w-4 h-4 animate-spin text-white" />
                      <span>Processing Sources & Extracting Evidence...</span>
                    </>
                  ) : (
                    <>
                      <Sparkles className="w-4 h-4 text-indigo-200" />
                      <span>Extract Structured Evidence</span>
                      <ArrowRight className="w-4 h-4 ml-1" />
                    </>
                  )}
                </button>
              </div>

              {/* Right Column: Structured Evidence Output Display */}
              <div className="lg:col-span-7 space-y-6">
                {!m4Response && !m4Loading && (
                  <div className="bg-slate-900/50 rounded-2xl border border-slate-800/80 p-12 text-center flex flex-col items-center justify-center min-h-[480px]">
                    <div className="w-16 h-16 rounded-2xl bg-slate-800/60 flex items-center justify-center text-slate-500 mb-4 border border-slate-700/50">
                      <Layers className="w-8 h-8 text-indigo-400/60" />
                    </div>
                    <h3 className="text-base font-semibold text-slate-300">Ready for Evidence Extraction</h3>
                    <p className="text-xs text-slate-500 max-w-sm mt-1">
                      Attach product sources on the left panel and click Extract Structured Evidence to view canonical attributes and provenance.
                    </p>
                  </div>
                )}

                {m4Loading && (
                  <div className="bg-slate-900/90 rounded-2xl border border-slate-800 p-12 text-center flex flex-col items-center justify-center min-h-[480px] space-y-4">
                    <div className="relative">
                      <div className="w-16 h-16 rounded-full border-4 border-indigo-500/20 border-t-indigo-500 animate-spin"></div>
                      <Cpu className="w-6 h-6 text-indigo-400 absolute inset-0 m-auto" />
                    </div>
                    <div>
                      <h3 className="text-base font-semibold text-slate-200">Executing Module 4 Pipeline</h3>
                      <p className="text-xs text-slate-400 mt-1">Intake -&gt; Document Processing -&gt; Hybrid Extraction -&gt; Canonical Mapping -&gt; Pydantic Validation...</p>
                    </div>
                  </div>
                )}

                {m4Response && (
                  <div className="space-y-6">
                    {/* Header Summary Card */}
                    <div className="bg-slate-900/90 rounded-2xl border border-slate-800 p-5 shadow-xl space-y-4">
                      <div className="flex items-center justify-between pb-3 border-b border-slate-800">
                        <div className="flex items-center space-x-3">
                          <span className="px-2.5 py-1 rounded-md text-xs font-bold bg-indigo-500/20 text-indigo-300 border border-indigo-500/30">
                            Structured Evidence
                          </span>
                          <span className="text-xs font-mono text-slate-400">
                            REQ: <strong className="text-slate-200">{m4Response.request_id}</strong>
                          </span>
                        </div>

                        <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold border ${
                          m4Response.status === 'SUCCESS'
                            ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20'
                            : 'bg-amber-500/10 text-amber-400 border-amber-500/20'
                        }`}>
                          <CheckCircle2 className="w-3.5 h-3.5 mr-1" />
                          {m4Response.status}
                        </span>
                      </div>

                      {/* Processing Stats Bar */}
                      <div className="grid grid-cols-4 gap-2 text-center text-xs">
                        <div className="bg-slate-950 p-2.5 rounded-xl border border-slate-800">
                          <span className="text-slate-500 block text-[10px] uppercase font-semibold">Sources Received</span>
                          <strong className="text-slate-200 text-sm">{m4Response.processing_summary?.sources_received || 0}</strong>
                        </div>
                        <div className="bg-slate-950 p-2.5 rounded-xl border border-slate-800">
                          <span className="text-slate-500 block text-[10px] uppercase font-semibold">Processed</span>
                          <strong className="text-indigo-300 text-sm">{m4Response.processing_summary?.sources_processed || 0}</strong>
                        </div>
                        <div className="bg-slate-950 p-2.5 rounded-xl border border-slate-800">
                          <span className="text-slate-500 block text-[10px] uppercase font-semibold">Attributes Extracted</span>
                          <strong className="text-emerald-400 text-sm">{m4Response.processing_summary?.attributes_extracted || 0}</strong>
                        </div>
                        <div className="bg-slate-950 p-2.5 rounded-xl border border-slate-800">
                          <span className="text-slate-500 block text-[10px] uppercase font-semibold">Time (Sec)</span>
                          <strong className="text-violet-300 text-sm">{m4Response.processing_summary?.processing_time_seconds || 0}s</strong>
                        </div>
                      </div>
                    </div>

                    {/* Extracted Attributes Table */}
                    <div className="bg-slate-900/90 rounded-2xl border border-slate-800 p-5 shadow-xl space-y-4">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center space-x-2">
                          <ShieldCheck className="w-4 h-4 text-emerald-400" />
                          <h4 className="text-xs font-semibold text-slate-300 uppercase tracking-wider">
                            Traceable Extracted Attributes ({m4Response.attributes?.length || 0})
                          </h4>
                        </div>
                      </div>

                      <div className="overflow-x-auto max-h-[360px] overflow-y-auto rounded-xl border border-slate-800">
                        <table className="w-full text-left text-xs text-slate-300">
                          <thead className="bg-slate-950 text-slate-400 uppercase text-[10px] sticky top-0 border-b border-slate-800">
                            <tr>
                              <th className="px-3.5 py-2.5">Canonical Attribute</th>
                              <th className="px-3.5 py-2.5">Extracted Value</th>
                              <th className="px-3.5 py-2.5">Source & Location</th>
                              <th className="px-3.5 py-2.5">Method</th>
                              <th className="px-3.5 py-2.5">Confidence</th>
                            </tr>
                          </thead>
                          <tbody className="divide-y divide-slate-800/60 bg-slate-950/40">
                            {m4Response.attributes?.length === 0 ? (
                              <tr>
                                <td colSpan={5} className="text-center py-6 text-slate-500 italic">No attributes extracted from provided sources.</td>
                              </tr>
                            ) : (
                              m4Response.attributes?.map((attr, idx) => (
                                <tr key={idx} className="hover:bg-slate-900/80 transition-colors">
                                  <td className="px-3.5 py-2.5 font-semibold text-indigo-300 font-mono">
                                    {attr.attribute}
                                    {attr.raw_attribute_name && (
                                      <span className="block text-[10px] font-normal text-slate-500">{attr.raw_attribute_name}</span>
                                    )}
                                  </td>
                                  <td className="px-3.5 py-2.5">
                                    <strong className="text-slate-100 font-mono">
                                      {Array.isArray(attr.value) ? attr.value.join(', ') : attr.value}
                                    </strong>
                                    {attr.unit && <span className="ml-1 text-slate-400 text-[11px] font-medium">{attr.unit}</span>}
                                  </td>
                                  <td className="px-3.5 py-2.5 text-slate-400">
                                    <span className="px-1.5 py-0.5 rounded bg-slate-800 text-[10px] text-slate-300 font-mono mr-1">
                                      {attr.source_id}
                                    </span>
                                    {attr.page && <span className="text-[11px] text-slate-400">Pg {attr.page}</span>}
                                    {attr.section && <span className="block text-[10px] text-slate-500 truncate max-w-[120px]">{attr.section}</span>}
                                  </td>
                                  <td className="px-3.5 py-2.5">
                                    <span className="px-2 py-0.5 rounded-full text-[10px] font-medium bg-indigo-500/10 text-indigo-300 border border-indigo-500/20">
                                      {attr.extraction_method}
                                    </span>
                                  </td>
                                  <td className="px-3.5 py-2.5">
                                    <span className="font-semibold text-emerald-400">
                                      {Math.round(attr.extraction_confidence * 100)}%
                                    </span>
                                  </td>
                                </tr>
                              ))
                            )}
                          </tbody>
                        </table>
                      </div>
                    </div>

                    {/* JSON Viewer */}
                    <div className="bg-slate-900/90 rounded-2xl border border-slate-800 p-5 shadow-xl space-y-3">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center space-x-2">
                          <Code className="w-4 h-4 text-indigo-400" />
                          <h4 className="text-xs font-semibold text-slate-300 uppercase tracking-wider">
                            Structured Evidence Schema Output (JSON)
                          </h4>
                        </div>
                        <button
                          type="button"
                          onClick={() => {
                            navigator.clipboard.writeText(JSON.stringify(m4Response, null, 2));
                            setM4Copied(true);
                            setTimeout(() => setM4Copied(false), 2000);
                          }}
                          className="inline-flex items-center space-x-1 text-xs px-2.5 py-1 rounded-md bg-slate-800 hover:bg-slate-700 text-slate-300 border border-slate-700 transition-colors"
                        >
                          {m4Copied ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5 text-slate-400" />}
                          <span>{m4Copied ? 'Copied' : 'Copy JSON'}</span>
                        </button>
                      </div>

                      <div className="bg-slate-950 rounded-xl p-4 border border-slate-800 max-h-[300px] overflow-auto">
                        <pre className="text-xs font-mono text-indigo-200 leading-relaxed whitespace-pre-wrap break-words">
                          {JSON.stringify(m4Response, null, 2)}
                        </pre>
                      </div>
                    </div>

                  </div>
                )}
              </div>

            </div>
          </div>
        )}

        {/* MODULE 1 VIEW */}
        {activeModule === 'MODULE1' && (
          <div className="space-y-6">
            <section className="bg-gradient-to-r from-slate-900 via-indigo-950/40 to-slate-900 rounded-2xl p-6 border border-slate-800 shadow-xl relative overflow-hidden">
              <div className="relative z-10 space-y-2">
                <h2 className="text-2xl font-bold text-white tracking-tight">Product Intake Studio (Module 1)</h2>
                <p className="text-sm text-slate-300 max-w-3xl leading-relaxed">
                  Ingest raw product datasets (CSV, PDF) row-by-row into standardized <code className="px-2 py-0.5 rounded bg-slate-800 text-indigo-300 text-xs font-mono border border-slate-700">StandardProductInput</code> objects preserving raw & normalized records.
                </p>
              </div>
            </section>

            <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
              {/* Left Form Column */}
              <div className="lg:col-span-5 space-y-6">
                <div className="bg-slate-900/90 rounded-2xl border border-slate-800 p-6 shadow-xl space-y-6">
                  <div>
                    <label className="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-3">1. Select Input Type</label>
                    <div className="grid grid-cols-5 gap-2 bg-slate-950 p-1.5 rounded-xl border border-slate-800">
                      {[
                        { id: 'CSV', label: 'CSV', icon: FileSpreadsheet },
                        { id: 'PDF', label: 'PDF', icon: FileText },
                        { id: 'URL', label: 'URL', icon: LinkIcon },
                        { id: 'JSON', label: 'JSON', icon: Code },
                        { id: 'PRODUCT_NAME', label: 'Name', icon: Tag }
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
                            }}
                            className={`flex flex-col items-center justify-center py-2.5 px-1 rounded-lg text-xs font-semibold transition-all ${
                              m1Tab === tab.id
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
                        <input type="file" accept=".pdf" onChange={(e) => { setM1File(e.target.files?.[0]); setM1Response(null); }} className="absolute inset-0 opacity-0 cursor-pointer w-full h-full" />
                        <UploadCloud className="w-10 h-10 text-indigo-400 mx-auto mb-2" />
                        <p className="text-sm font-medium text-slate-200">{m1File?.name || 'Click or Drag PDF file here'}</p>
                      </div>
                    )}

                    {m1Tab === 'URL' && (
                      <input type="url" value={m1Url} onChange={(e) => setM1Url(e.target.value)} placeholder="https://example.com/product" className="w-full bg-slate-950 border border-slate-800 rounded-xl p-3 text-sm text-slate-100 font-mono focus:border-indigo-500 focus:outline-none" />
                    )}

                    {m1Tab === 'JSON' && (
                      <textarea rows={6} value={m1JsonText} onChange={(e) => setM1JsonText(e.target.value)} placeholder='{"product_name": "SKF 6205"}' className="w-full bg-slate-950 border border-slate-800 rounded-xl p-3 text-xs font-mono text-indigo-300 focus:border-indigo-500 focus:outline-none" />
                    )}

                    {m1Tab === 'PRODUCT_NAME' && (
                      <textarea rows={4} value={m1ProductName} onChange={(e) => setM1ProductName(e.target.value)} placeholder="Enter raw product title or specs" className="w-full bg-slate-950 border border-slate-800 rounded-xl p-3 text-sm text-slate-100 focus:border-indigo-500 focus:outline-none" />
                    )}

                    {m1Error && (
                      <div className="p-3 bg-rose-500/10 border border-rose-500/30 rounded-xl text-rose-300 text-xs flex items-center space-x-2">
                        <AlertCircle className="w-4 h-4 text-rose-400 shrink-0" />
                        <span>{m1Error}</span>
                      </div>
                    )}

                    <button type="submit" disabled={m1Loading} className="w-full py-3.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white font-semibold text-sm shadow-lg flex items-center justify-center space-x-2 transition-all">
                      {m1Loading ? <RefreshCw className="w-4 h-4 animate-spin text-white" /> : <span>Process Product Input</span>}
                    </button>
                  </form>
                </div>
              </div>

              {/* Right Output / Results Column */}
              <div className="lg:col-span-7 space-y-6">
                {!m1Response && !m1Loading && (
                  <div className="bg-slate-900/60 rounded-2xl border border-slate-800/80 p-12 text-center text-slate-500 space-y-3">
                    <Box className="w-12 h-12 text-slate-700 mx-auto" />
                    <h3 className="text-sm font-semibold text-slate-400">Ready for Product Intake</h3>
                    <p className="text-xs text-slate-500 max-w-sm mx-auto">
                      Upload a CSV dataset or PDF document to extract candidate product identities and view generated StandardProductInput objects.
                    </p>
                  </div>
                )}

                {/* Batch Response View (CSV multi-row) */}
                {m1Response && m1Response.items && (
                  <div className="space-y-6">
                    {/* Batch Summary Cards */}
                    <div className="grid grid-cols-4 gap-3">
                      <div className="bg-slate-900 border border-slate-800 rounded-xl p-3 text-center">
                        <span className="text-[10px] font-semibold uppercase text-slate-400 block">Total Rows</span>
                        <span className="text-xl font-bold text-slate-100">{m1Response.total_rows}</span>
                      </div>
                      <div className="bg-slate-900 border border-slate-800 rounded-xl p-3 text-center">
                        <span className="text-[10px] font-semibold uppercase text-slate-400 block">Processed</span>
                        <span className="text-xl font-bold text-emerald-400">{m1Response.processed_count}</span>
                      </div>
                      <div className="bg-slate-900 border border-slate-800 rounded-xl p-3 text-center">
                        <span className="text-[10px] font-semibold uppercase text-slate-400 block">Successful</span>
                        <span className="text-xl font-bold text-indigo-400">{m1Response.successful_count}</span>
                      </div>
                      <div className="bg-slate-900 border border-slate-800 rounded-xl p-3 text-center">
                        <span className="text-[10px] font-semibold uppercase text-slate-400 block">Failed</span>
                        <span className="text-xl font-bold text-rose-400">{m1Response.failed_count}</span>
                      </div>
                    </div>

                    {/* Products Row Table */}
                    <div className="bg-slate-900/90 rounded-2xl border border-slate-800 p-5 shadow-xl space-y-3">
                      <div className="flex items-center justify-between">
                        <h4 className="text-xs font-semibold text-slate-300 uppercase tracking-wider">
                          Processed Product Records ({m1Response.items.length})
                        </h4>
                        <span className="text-xs text-slate-500 font-mono">Click a row to view JSON</span>
                      </div>

                      <div className="border border-slate-800 rounded-xl overflow-hidden max-h-[240px] overflow-y-auto">
                        <table className="w-full text-left border-collapse text-xs">
                          <thead>
                            <tr className="bg-slate-950 text-slate-400 border-b border-slate-800 font-mono text-[11px]">
                              <th className="px-3 py-2">Row</th>
                              <th className="px-3 py-2">SKU / Part #</th>
                              <th className="px-3 py-2">Desc / Product Name</th>
                              <th className="px-3 py-2">Brand</th>
                              <th className="px-3 py-2">Status</th>
                            </tr>
                          </thead>
                          <tbody className="divide-y divide-slate-800/60 font-mono">
                            {m1Response.items.map((item, idx) => {
                              const isSelected = idx === m1SelectedRowIndex;
                              const rowNum = item.source_record?.row_number || idx + 1;
                              return (
                                <tr
                                  key={item.request_id}
                                  onClick={() => setM1SelectedRowIndex(idx)}
                                  className={`cursor-pointer transition-colors ${
                                    isSelected ? 'bg-indigo-950/60 border-l-2 border-indigo-500' : 'hover:bg-slate-800/50'
                                  }`}
                                >
                                  <td className="px-3 py-2 font-semibold text-slate-400">#{rowNum}</td>
                                  <td className="px-3 py-2 font-semibold text-indigo-300">{item.identity?.sku || item.identity?.part_number || '-'}</td>
                                  <td className="px-3 py-2 text-slate-300 max-w-[200px] truncate">{item.identity?.product_name || '-'}</td>
                                  <td className="px-3 py-2 text-slate-400">{item.identity?.brand || '-'}</td>
                                  <td className="px-3 py-2">
                                    <span className={`px-2 py-0.5 rounded text-[10px] font-semibold ${
                                      item.status === 'READY_FOR_RESOLUTION' ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20' : 'bg-slate-800 text-slate-400'
                                    }`}>
                                      {item.status}
                                    </span>
                                  </td>
                                </tr>
                              );
                            })}
                          </tbody>
                        </table>
                      </div>
                    </div>

                    {/* Selected Row JSON Inspector */}
                    {m1Response.items[m1SelectedRowIndex] && (
                      <div className="bg-slate-900/90 rounded-2xl border border-slate-800 p-5 shadow-xl space-y-3">
                        <div className="flex items-center justify-between">
                          <div className="flex items-center space-x-2">
                            <Code className="w-4 h-4 text-indigo-400" />
                            <h4 className="text-xs font-semibold text-slate-300 uppercase tracking-wider">
                              StandardProductInput JSON — Row #{m1Response.items[m1SelectedRowIndex].source_record?.row_number || (m1SelectedRowIndex + 1)} ({m1Response.items[m1SelectedRowIndex].request_id})
                            </h4>
                          </div>
                          <button
                            type="button"
                            onClick={() => {
                              navigator.clipboard.writeText(JSON.stringify(m1Response.items[m1SelectedRowIndex], null, 2));
                              setM1Copied(true);
                              setTimeout(() => setM1Copied(false), 2000);
                            }}
                            className="inline-flex items-center space-x-1 text-xs px-2.5 py-1 rounded-md bg-slate-800 hover:bg-slate-700 text-slate-300 border border-slate-700 transition-colors"
                          >
                            {m1Copied ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5 text-slate-400" />}
                            <span>{m1Copied ? 'Copied' : 'Copy JSON'}</span>
                          </button>
                        </div>
                        <div className="bg-slate-950 rounded-xl p-4 border border-slate-800 max-h-[350px] overflow-auto">
                          <pre className="text-xs font-mono text-indigo-200 leading-relaxed whitespace-pre-wrap">
                            {JSON.stringify(m1Response.items[m1SelectedRowIndex], null, 2)}
                          </pre>
                        </div>
                      </div>
                    )}
                  </div>
                )}

                {/* Single Item Response View (PDF, URL, JSON, PRODUCT_NAME) */}
                {m1Response && !m1Response.items && (
                  <div className="bg-slate-900/90 rounded-2xl border border-slate-800 p-5 shadow-xl space-y-3">
                    <div className="flex items-center justify-between">
                      <h4 className="text-xs font-semibold text-slate-300 uppercase tracking-wider">Module 1 Standard Product Input JSON</h4>
                      <button
                        type="button"
                        onClick={() => {
                          navigator.clipboard.writeText(JSON.stringify(m1Response, null, 2));
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
                        {JSON.stringify(m1Response, null, 2)}
                      </pre>
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>
        )}

      </main>

      {/* Footer */}
      <footer className="border-t border-slate-900 bg-slate-950 py-4 px-6 text-center text-xs text-slate-600">
        ProductDNA Intelligence Platform &bull; Module 4 Implementation &bull; Evidence Collection & Structured Extraction Engine
      </footer>
    </div>
  );
}
