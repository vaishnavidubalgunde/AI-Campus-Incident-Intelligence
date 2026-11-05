import React, { useState } from 'react';
import { intelligenceService } from '../services/api';
import { AssistantResponse } from '../types';
import {
  MessageSquareCode,
  Send,
  Sparkles,
  Bot,
  User,
  ArrowRight,
  HelpCircle,
  Database,
  ExternalLink
} from 'lucide-react';
import { Link } from 'react-router-dom';

interface ChatMessage {
  id: string;
  sender: 'user' | 'assistant';
  text: string;
  responseObj?: AssistantResponse;
}

export const AssistantChat: React.FC = () => {
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      id: '1',
      sender: 'assistant',
      text: "Hello! I am your Campus Incident Analytics Assistant. Ask me any analytical question about our campus incident database, such as location hotspots, urgent electrical risks, team workloads, or recurring issues.",
    },
  ]);
  const [inputQuery, setInputQuery] = useState('');
  const [loading, setLoading] = useState(false);

  const samplePrompts = [
    'Which block has the highest number of incidents?',
    'Show all critical electrical incidents.',
    'How many water leakage incidents are unresolved?',
    'Which department has the highest pending workload?',
    'What should the maintenance team prioritize?',
    'Summarize recurring campus problems.',
  ];

  const handleSendQuery = async (queryText: string) => {
    if (!queryText.trim() || loading) return;
    const userMsg: ChatMessage = {
      id: Date.now().toString(),
      sender: 'user',
      text: queryText,
    };
    setMessages((prev) => [...prev, userMsg]);
    setInputQuery('');
    setLoading(true);

    try {
      const res = await intelligenceService.queryAssistant(queryText);
      const assistantMsg: ChatMessage = {
        id: (Date.now() + 1).toString(),
        sender: 'assistant',
        text: res.answer,
        responseObj: res,
      };
      setMessages((prev) => [...prev, assistantMsg]);
    } catch (e) {
      setMessages((prev) => [
        ...prev,
        {
          id: (Date.now() + 1).toString(),
          sender: 'assistant',
          text: 'Sorry, I encountered an error querying the campus database. Please ensure the backend is running.',
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6 max-w-5xl mx-auto">
      {/* Header */}
      <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-xs flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-xl font-bold text-slate-900 flex items-center space-x-2">
            <MessageSquareCode className="w-5 h-5 text-blue-600" />
            <span>Natural-Language Analytics Assistant</span>
          </h1>
          <p className="text-xs text-slate-500">
            Ask natural language questions evaluated directly against the live SQLite campus incident repository.
          </p>
        </div>

        <div className="flex items-center space-x-1.5 text-xs text-emerald-700 bg-emerald-50 px-3 py-1 rounded-full border border-emerald-200 font-semibold self-start sm:self-auto">
          <Database className="w-3.5 h-3.5" />
          <span>Parameterized Safe SQL</span>
        </div>
      </div>

      {/* Suggested Chips */}
      <div className="bg-white rounded-2xl border border-slate-200 p-4 shadow-xs space-y-2">
        <span className="text-[11px] font-bold text-slate-400 uppercase tracking-wider block">
          Suggested Analytics Inquiries (Click to ask):
        </span>
        <div className="flex flex-wrap gap-2">
          {samplePrompts.map((prompt) => (
            <button
              key={prompt}
              onClick={() => handleSendQuery(prompt)}
              className="px-3 py-1.5 bg-slate-50 hover:bg-blue-50 hover:text-blue-700 hover:border-blue-200 text-slate-700 rounded-lg text-xs font-medium border border-slate-200 transition-colors text-left"
            >
              {prompt}
            </button>
          ))}
        </div>
      </div>

      {/* Chat Area */}
      <div className="bg-white rounded-2xl border border-slate-200 shadow-xs flex flex-col h-[520px] overflow-hidden">
        <div className="flex-1 p-6 overflow-y-auto space-y-5">
          {messages.map((m) => {
            const isBot = m.sender === 'assistant';

            return (
              <div
                key={m.id}
                className={`flex items-start space-x-3 ${isBot ? '' : 'flex-row-reverse space-x-reverse'}`}
              >
                <div
                  className={`w-8 h-8 rounded-full flex items-center justify-center shrink-0 ${
                    isBot ? 'bg-gradient-to-tr from-blue-700 to-indigo-600 text-white' : 'bg-slate-200 text-slate-700'
                  }`}
                >
                  {isBot ? <Bot className="w-4 h-4" /> : <User className="w-4 h-4" />}
                </div>

                <div
                  className={`max-w-2xl rounded-2xl p-4 text-xs leading-relaxed ${
                    isBot
                      ? 'bg-slate-50 border border-slate-200 text-slate-800'
                      : 'bg-blue-600 text-white shadow-xs'
                  }`}
                >
                  <p className="whitespace-pre-line font-medium text-sm sm:text-xs">{m.text}</p>

                  {/* If assistant returned structured data */}
                  {m.responseObj && (
                    <div className="mt-3 pt-3 border-t border-slate-200 space-y-2.5">
                      {/* Intent & Follow-ups */}
                      <div className="flex flex-wrap items-center gap-2 text-[10px]">
                        <span className="font-bold text-slate-500 uppercase">Intent:</span>
                        <span className="font-mono bg-blue-100 text-blue-800 px-2 py-0.5 rounded">
                          {m.responseObj.intent_detected}
                        </span>
                      </div>

                      {/* Relevant incidents links */}
                      {m.responseObj.relevant_incident_ids.length > 0 && (
                        <div className="text-[11px] space-y-1">
                          <span className="text-slate-500 font-semibold block">Relevant Incident IDs:</span>
                          <div className="flex flex-wrap gap-1.5">
                            {m.responseObj.relevant_incident_ids.map((incId) => (
                              <Link
                                key={incId}
                                to={`/incidents/${incId}`}
                                className="inline-flex items-center space-x-1 px-2 py-0.5 bg-white border border-slate-200 hover:border-blue-400 text-blue-700 rounded text-[11px] font-bold shadow-2xs transition-colors"
                              >
                                <span>#{incId}</span>
                                <ExternalLink className="w-2.5 h-2.5" />
                              </Link>
                            ))}
                          </div>
                        </div>
                      )}

                      {/* Follow-up suggestions */}
                      {m.responseObj.suggested_followups.length > 0 && (
                        <div className="text-[11px] space-y-1 pt-1 border-t border-slate-200/60">
                          <span className="text-slate-500 font-semibold block">Follow-up Queries:</span>
                          <div className="flex flex-wrap gap-1.5">
                            {m.responseObj.suggested_followups.map((f, idx) => (
                              <button
                                key={idx}
                                onClick={() => handleSendQuery(f)}
                                className="text-blue-600 hover:underline text-[11px] font-medium text-left"
                              >
                                → {f}
                              </button>
                            ))}
                          </div>
                        </div>
                      )}
                    </div>
                  )}
                </div>
              </div>
            );
          })}

          {loading && (
            <div className="flex items-center space-x-3 text-xs text-slate-400">
              <div className="w-8 h-8 rounded-full bg-blue-600 text-white flex items-center justify-center">
                <Bot className="w-4 h-4" />
              </div>
              <div className="bg-slate-50 border border-slate-200 p-3 rounded-xl flex items-center space-x-2">
                <div className="w-2 h-2 rounded-full bg-blue-600 animate-bounce" />
                <div className="w-2 h-2 rounded-full bg-blue-600 animate-bounce [animation-delay:0.2s]" />
                <div className="w-2 h-2 rounded-full bg-blue-600 animate-bounce [animation-delay:0.4s]" />
                <span className="text-[11px] text-slate-500 font-medium ml-1">Analyzing database records...</span>
              </div>
            </div>
          )}
        </div>

        {/* Input box */}
        <div className="p-4 bg-slate-50 border-t border-slate-200">
          <form
            onSubmit={(e) => {
              e.preventDefault();
              handleSendQuery(inputQuery);
            }}
            className="flex items-center space-x-2"
          >
            <input
              type="text"
              placeholder="Ask an analytical question about incidents, locations, or response backlogs..."
              value={inputQuery}
              onChange={(e) => setInputQuery(e.target.value)}
              className="flex-1 px-4 py-2.5 rounded-xl border border-slate-300 text-xs focus:ring-2 focus:ring-blue-500 outline-hidden bg-white"
            />
            <button
              type="submit"
              disabled={loading || !inputQuery.trim()}
              className="px-4 py-2.5 bg-blue-600 hover:bg-blue-700 text-white rounded-xl text-xs font-bold shadow-xs transition-colors disabled:opacity-50 flex items-center space-x-1"
            >
              <Send className="w-3.5 h-3.5" />
              <span>Ask</span>
            </button>
          </form>
        </div>
      </div>
    </div>
  );
};
