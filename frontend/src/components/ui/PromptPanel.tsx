'use client';

/**
 * === PANEL PROMPTU AMBASADORA ===
 *
 * Input dla zapytań ambasadora z możliwością attachmentów
 */

import { useState, useRef } from 'react';
import { Card } from '@/components/ui/card';
import { Send, Paperclip, X, MessageSquare, Loader2, File } from 'lucide-react';
import { cn } from '@/lib/utils';

interface PromptPanelProps {
  onSubmit: (prompt: string, attachments?: File[]) => void;
  isProcessing?: boolean;
  placeholder?: string;
}

export default function PromptPanel({
  onSubmit,
  isProcessing = false,
  placeholder = 'Wprowadź zapytanie analityczne...',
}: PromptPanelProps) {
  const [prompt, setPrompt] = useState('');
  const [attachments, setAttachments] = useState<File[]>([]);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleSubmit = () => {
    if (!prompt.trim() || isProcessing) return;
    onSubmit(prompt, attachments);
    setPrompt('');
    setAttachments([]);
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = Array.from(e.target.files || []);
    setAttachments(prev => [...prev, ...files]);
  };

  const removeAttachment = (index: number) => {
    setAttachments(prev => prev.filter((_, i) => i !== index));
  };

  return (
    <Card className="p-4 bg-white border-slate-200 shadow-sm">
      {/* Header */}
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-2">
          <div className="w-2 h-2 rounded-full bg-blue-500 animate-pulse" />
          <span className="text-xs font-bold text-slate-600 tracking-wider uppercase">
            Zapytanie ambasadora
          </span>
        </div>
        <span className="text-[10px] text-slate-400 font-medium bg-slate-50 px-2 py-0.5 rounded">
          Enter = wyślij • Shift+Enter = nowa linia
        </span>
      </div>

      {/* Attachments */}
      {attachments.length > 0 && (
        <div className="flex flex-wrap gap-2 mb-3">
          {attachments.map((file, i) => (
            <div
              key={i}
              className="flex items-center gap-2 px-2 py-1.5 rounded-md bg-slate-50 border border-slate-200"
            >
              <File className="w-3 h-3 text-slate-400" />
              <span className="text-xs text-slate-600 max-w-[100px] truncate font-medium">
                {file.name}
              </span>
              <button
                onClick={() => removeAttachment(i)}
                className="text-slate-400 hover:text-red-500 transition-colors"
              >
                <X className="w-3 h-3" />
              </button>
            </div>
          ))}
        </div>
      )}

      {/* Input area */}
      <div className="relative">
        <textarea
          value={prompt}
          onChange={(e) => setPrompt(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder={placeholder}
          disabled={isProcessing}
          rows={3}
          className="w-full px-4 py-3 pr-24 rounded-lg bg-slate-50 border border-slate-200 text-slate-800 placeholder:text-slate-400 resize-none focus:outline-none focus:border-blue-400 focus:ring-2 focus:ring-blue-100 transition-all text-sm"
        />

        {/* Actions */}
        <div className="absolute bottom-3 right-3 flex items-center gap-2">
          {/* Attachment button */}
          <input
            ref={fileInputRef}
            type="file"
            multiple
            onChange={handleFileSelect}
            className="hidden"
            accept=".pdf,.doc,.docx,.txt,.csv,.json"
          />
          <button
            onClick={() => fileInputRef.current?.click()}
            className="p-2 rounded-md hover:bg-slate-200 text-slate-400 hover:text-slate-600 transition-colors"
            title="Dodaj załącznik"
          >
            <Paperclip className="w-4 h-4" />
          </button>

          {/* Submit button */}
          <button
            onClick={handleSubmit}
            disabled={!prompt.trim() || isProcessing}
            className={cn(
              "p-2 rounded-md transition-all shadow-sm",
              prompt.trim() && !isProcessing
                ? "bg-[#192355] text-white hover:bg-blue-900 hover:shadow-md active:scale-95"
                : "bg-slate-200 text-slate-400 cursor-not-allowed"
            )}
          >
            {isProcessing ? (
              <Loader2 className="w-4 h-4 animate-spin" />
            ) : (
              <Send className="w-4 h-4" />
            )}
          </button>
        </div>
      </div>

      {/* Quick prompts */}
      <div className="flex flex-wrap gap-2 mt-3">
        {[
          'Analiza sytuacji w regionie',
          'Prognoza konfliktów',
          'Wpływ sankcji',
          'Relacje bilateralne',
        ].map((suggestion) => (
          <button
            key={suggestion}
            onClick={() => setPrompt(suggestion + ': ')}
            className="flex items-center gap-1.5 px-2.5 py-1.5 text-[10px] font-medium rounded border border-slate-200 bg-white text-slate-500 hover:border-blue-300 hover:text-blue-600 hover:bg-blue-50 transition-colors"
          >
            <MessageSquare className="w-3 h-3 opacity-50" />
            {suggestion}
          </button>
        ))}
      </div>
    </Card>
  );
}