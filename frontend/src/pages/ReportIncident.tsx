import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { incidentService, metadataService, systemService } from '../services/api';
import { IncidentCategory, AIAnalysisSummary, DuplicateMatch } from '../types';
import { SeverityBadge } from '../components/SeverityBadge';
import {
  Sparkles,
  Upload,
  AlertTriangle,
  CheckCircle,
  Building2,
  MapPin,
  Tag,
  ShieldCheck,
  Send,
  Eye,
  Info
} from 'lucide-react';

export const ReportIncident: React.FC = () => {
  const navigate = useNavigate();
  const [categories, setCategories] = useState<IncidentCategory[]>([]);
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [building, setBuilding] = useState('Block C');
  const [location, setLocation] = useState('');
  const [floorRoom, setFloorRoom] = useState('');
  const [categoryId, setCategoryId] = useState<number | undefined>(undefined);
  const [isAnonymous, setIsAnonymous] = useState(false);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [photoUrl, setPhotoUrl] = useState<string | null>(null);

  const [aiPreview, setAiPreview] = useState<any>(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  const campusBuildings = [
    'Block C',
    'Central Library',
    'Block A',
    'Block B',
    'Block E',
    'Cafeteria',
    'Hostel 1',
    'Hostel 2',
    'Auditorium',
    'Sports Complex',
    'Admin Block',
  ];

  useEffect(() => {
    metadataService.getCategories().then(setCategories).catch(console.error);
  }, []);

  // Trigger AI preview when description is entered
  const handleAnalyzeDraft = async () => {
    if (!description.trim() || description.length < 5) return;
    setIsAnalyzing(true);
    try {
      const res = await incidentService.previewAI({
        title: title || 'Campus Incident',
        description,
        building,
        location: location || building,
      });
      setAiPreview(res);
      // Auto-suggest category if not manually overridden
      if (!categoryId && res.predicted_category) {
        const matched = categories.find((c) => c.name === res.predicted_category);
        if (matched) setCategoryId(matched.id);
      }
    } catch (e) {
      console.error(e);
    } finally {
      setIsAnalyzing(false);
    }
  };

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setSelectedFile(file);
    try {
      const uploadRes = await systemService.uploadPhoto(file);
      setPhotoUrl(uploadRes.photo_url);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Photo upload failed. Maximum 5MB.');
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setIsSubmitting(true);

    try {
      const created = await incidentService.create({
        title,
        description,
        location: location || building,
        building,
        floor_room: floorRoom || undefined,
        category_id: categoryId,
        is_anonymous: isAnonymous,
        photo_url: photoUrl || undefined,
      });

      setSuccess(`Incident successfully registered as ${created.incident_number}!`);
      setTimeout(() => {
        navigate(`/incidents/${created.id}`);
      }, 1200);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to submit incident report.');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="max-w-5xl mx-auto space-y-6">
      {/* Header */}
      <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-xs">
        <div className="flex items-center space-x-3">
          <div className="w-10 h-10 rounded-xl bg-blue-100 text-blue-700 flex items-center justify-center">
            <Sparkles className="w-5 h-5 text-blue-600" />
          </div>
          <div>
            <h1 className="text-xl font-bold text-slate-900">Report Campus Incident</h1>
            <p className="text-xs text-slate-500">
              Submit problem reports using natural language. The AI classification pipeline will automatically triage category, severity, and duplicates.
            </p>
          </div>
        </div>
      </div>

      {error && (
        <div className="p-4 rounded-xl bg-red-50 border border-red-200 text-xs text-red-700 flex items-center space-x-2">
          <AlertTriangle className="w-4 h-4 shrink-0 text-red-600" />
          <span>{error}</span>
        </div>
      )}

      {success && (
        <div className="p-4 rounded-xl bg-emerald-50 border border-emerald-200 text-xs text-emerald-800 flex items-center space-x-2 font-medium">
          <CheckCircle className="w-4 h-4 shrink-0 text-emerald-600" />
          <span>{success}</span>
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Form Container */}
        <div className="lg:col-span-7 bg-white rounded-2xl border border-slate-200 p-6 shadow-xs">
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1">
                Incident Title *
              </label>
              <input
                type="text"
                required
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                placeholder="e.g., Water leaking continuously from ceiling on 2nd floor"
                className="w-full px-3.5 py-2.5 rounded-lg border border-slate-300 text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-hidden"
              />
            </div>

            <div>
              <div className="flex items-center justify-between mb-1">
                <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider">
                  Detailed Description *
                </label>
                <button
                  type="button"
                  onClick={handleAnalyzeDraft}
                  disabled={isAnalyzing || description.length < 5}
                  className="text-xs text-blue-600 hover:text-blue-800 font-semibold flex items-center space-x-1 disabled:opacity-50"
                >
                  <Sparkles className="w-3.5 h-3.5" />
                  <span>{isAnalyzing ? 'Analyzing AI...' : 'Analyze with AI'}</span>
                </button>
              </div>
              <textarea
                required
                rows={4}
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                onBlur={handleAnalyzeDraft}
                placeholder="Describe the issue in your own words. Mention what happened, equipment involved, and any observable hazards..."
                className="w-full px-3.5 py-2.5 rounded-lg border border-slate-300 text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-hidden"
              />
              <span className="text-[11px] text-slate-400 block mt-0.5">
                Tip: Writing naturally helps the AI pipeline extract severity and identify duplicate records.
              </span>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1">
                  Campus Building / Zone *
                </label>
                <select
                  value={building}
                  onChange={(e) => setBuilding(e.target.value)}
                  className="w-full px-3.5 py-2.5 rounded-lg border border-slate-300 text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-hidden"
                >
                  {campusBuildings.map((b) => (
                    <option key={b} value={b}>
                      {b}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1">
                  Specific Location *
                </label>
                <input
                  type="text"
                  required
                  value={location}
                  onChange={(e) => setLocation(e.target.value)}
                  placeholder="e.g., Block C North Hallway"
                  className="w-full px-3.5 py-2.5 rounded-lg border border-slate-300 text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-hidden"
                />
              </div>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1">
                  Floor & Room Number
                </label>
                <input
                  type="text"
                  value={floorRoom}
                  onChange={(e) => setFloorRoom(e.target.value)}
                  placeholder="e.g., 2nd Floor, Room 204"
                  className="w-full px-3.5 py-2.5 rounded-lg border border-slate-300 text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-hidden"
                />
              </div>

              <div>
                <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1">
                  Category (Auto-Suggested)
                </label>
                <select
                  value={categoryId || ''}
                  onChange={(e) => setCategoryId(e.target.value ? Number(e.target.value) : undefined)}
                  className="w-full px-3.5 py-2.5 rounded-lg border border-slate-300 text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-hidden"
                >
                  <option value="">Let AI Classify Automatically</option>
                  {categories.map((c) => (
                    <option key={c.id} value={c.id}>
                      {c.name}
                    </option>
                  ))}
                </select>
              </div>
            </div>

            {/* Photo Attachment */}
            <div>
              <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1">
                Attach Photo (Optional)
              </label>
              <div className="flex items-center space-x-3">
                <label className="cursor-pointer px-4 py-2 bg-slate-100 hover:bg-slate-200 text-slate-700 rounded-lg text-xs font-semibold flex items-center space-x-2 border border-slate-200 transition-colors">
                  <Upload className="w-4 h-4 text-slate-500" />
                  <span>{selectedFile ? selectedFile.name : 'Choose Image (JPG, PNG)'}</span>
                  <input
                    type="file"
                    accept="image/jpeg,image/png,image/webp"
                    className="hidden"
                    onChange={handleFileUpload}
                  />
                </label>
                {photoUrl && (
                  <span className="text-xs text-emerald-600 font-semibold flex items-center space-x-1">
                    <CheckCircle className="w-3.5 h-3.5" />
                    <span>Attached</span>
                  </span>
                )}
              </div>
            </div>

            {/* Anonymous Toggle */}
            <div className="pt-2">
              <label className="flex items-center space-x-2.5 cursor-pointer">
                <input
                  type="checkbox"
                  checked={isAnonymous}
                  onChange={(e) => setIsAnonymous(e.target.checked)}
                  className="rounded border-slate-300 text-blue-600 focus:ring-blue-500 w-4 h-4"
                />
                <span className="text-xs text-slate-700 font-medium">
                  Submit anonymously (Reporter name will not be shown to other students)
                </span>
              </label>
            </div>

            <div className="pt-4 border-t border-slate-100">
              <button
                type="submit"
                disabled={isSubmitting}
                className="w-full py-3 px-4 rounded-xl bg-blue-600 hover:bg-blue-700 text-white font-bold text-sm shadow-md shadow-blue-500/20 transition-all flex items-center justify-center space-x-2 disabled:opacity-70"
              >
                {isSubmitting ? (
                  <span>Submitting & Processing AI...</span>
                ) : (
                  <>
                    <Send className="w-4 h-4" />
                    <span>Submit Incident Report</span>
                  </>
                )}
              </button>
            </div>
          </form>
        </div>

        {/* AI Intelligence Live Preview Panel */}
        <div className="lg:col-span-5 space-y-4">
          <div className="bg-gradient-to-br from-slate-900 to-indigo-950 text-white rounded-2xl p-6 shadow-md border border-slate-800">
            <div className="flex items-center justify-between pb-3 border-b border-white/10">
              <div className="flex items-center space-x-2">
                <Sparkles className="w-4 h-4 text-sky-400" />
                <h3 className="text-sm font-bold tracking-tight">AI Pre-Flight Intelligence</h3>
              </div>
              <span className="text-[10px] font-semibold bg-sky-500/20 text-sky-300 px-2 py-0.5 rounded-full border border-sky-400/30">
                Live NLP Pipeline
              </span>
            </div>

            {!aiPreview ? (
              <div className="py-10 text-center text-xs text-slate-400 space-y-2">
                <Info className="w-6 h-6 mx-auto text-slate-500" />
                <p>Type your incident description to view live AI predictions for:</p>
                <ul className="text-[11px] text-slate-300 space-y-1">
                  <li>• Category classification & confidence</li>
                  <li>• Severity level & transparent score factors</li>
                  <li>• Duplicate & recurrence detection</li>
                  <li>• Suggested response team routing</li>
                </ul>
              </div>
            ) : (
              <div className="mt-4 space-y-4 text-xs">
                {/* Predicted Category & Department */}
                <div className="bg-white/5 rounded-xl p-3 border border-white/10 space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="text-slate-400">Predicted Category:</span>
                    <span className="font-bold text-white text-sm">{aiPreview.predicted_category}</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-slate-400">Confidence Band:</span>
                    <span className="font-semibold text-sky-300">
                      {(aiPreview.confidence_score * 100).toFixed(0)}% Match
                    </span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-slate-400">Target Department:</span>
                    <span className="font-semibold text-slate-200">{aiPreview.suggested_department}</span>
                  </div>
                </div>

                {/* Severity & Score Factors */}
                <div className="bg-white/5 rounded-xl p-3 border border-white/10 space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="text-slate-400">Calculated Severity:</span>
                    <SeverityBadge severity={aiPreview.severity_level} />
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-slate-400">Priority Score:</span>
                    <span className="font-bold text-amber-300 text-sm">
                      {aiPreview.priority_score} / 100
                    </span>
                  </div>
                  <div className="mt-2 pt-2 border-t border-white/10">
                    <span className="text-[10px] uppercase font-bold text-slate-400 block mb-1">
                      Transparent Factor Audit:
                    </span>
                    <ul className="space-y-1 text-[11px] text-slate-300">
                      {aiPreview.score_factors?.map((f: string, idx: number) => (
                        <li key={idx} className="flex items-start space-x-1.5">
                          <span className="text-sky-400">•</span>
                          <span>{f}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                </div>

                {/* Duplicate / Recurrence Alert */}
                {aiPreview.duplicates_found && aiPreview.duplicates_found.length > 0 && (
                  <div className="bg-amber-500/10 border border-amber-500/30 rounded-xl p-3 space-y-2">
                    <div className="flex items-center space-x-1.5 text-amber-400 font-bold">
                      <AlertTriangle className="w-4 h-4" />
                      <span>Possible Duplicate or Recurring Issue</span>
                    </div>
                    <p className="text-[11px] text-amber-200/80 leading-relaxed">
                      AI identified {aiPreview.duplicates_found.length} existing report(s) describing similar problems in {building}.
                    </p>
                    <div className="space-y-1 mt-1">
                      {aiPreview.duplicates_found.slice(0, 2).map((dup: DuplicateMatch) => (
                        <div key={dup.incident_id} className="text-[11px] bg-black/20 p-2 rounded text-slate-200 flex justify-between">
                          <span className="truncate max-w-[180px]">{dup.title}</span>
                          <span className="font-bold text-amber-300 shrink-0">
                            {(dup.similarity_score * 100).toFixed(0)}% Sim
                          </span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* AI Summary */}
                <div className="text-[11px] text-slate-400 italic bg-black/20 p-2.5 rounded-lg border border-white/5">
                  "{aiPreview.summary}"
                </div>

                <div className="text-[10px] text-slate-400 pt-2 border-t border-white/10">
                  Notice: AI analysis acts as assistive decision support and will be verified by university maintenance controllers.
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
