"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Download, BarChart3, Table, Copy, Check } from "lucide-react";
import { ChatResponse } from "@/types/chat";
import DataTable from "./DataTable";
import ChartView from "./ChartView";

interface ChatMessageProps {
  message: ChatResponse;
  onDownload: () => void;
}

export default function ChatMessage({ message, onDownload }: ChatMessageProps) {
  const [viewMode, setViewMode] = useState<'table' | 'chart'>('table');
  const [copied, setCopied] = useState(false);

  const hasTable = message.rows && message.rows.length > 0;
  const hasChart = hasTable && (message.chart_suggestion === 'bar' || message.chart_suggestion === 'line' || message.chart_suggestion === 'pie');

  const copyToClipboard = async (text: string) => {
    try {
      await navigator.clipboard.writeText(text);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (err) {
      console.error('클립보드 복사 실패:', err);
    }
  };

  return (
    <div className="bg-gray-50 rounded-lg p-4 space-y-4">
      {/* 답변 텍스트 */}
      <div className="text-gray-900">
        {message.answer_text}
      </div>

      {/* SQL 코드 블록 */}
      {message.sql && (
        <div className="bg-gray-900 rounded-md p-3">
          <div className="flex items-center justify-between mb-2">
            <span className="text-gray-300 text-sm font-mono">SQL</span>
            <Button
              variant="ghost"
              size="sm"
              onClick={() => copyToClipboard(message.sql)}
              className="h-6 px-2 text-gray-400 hover:text-white"
            >
              {copied ? <Check className="w-3 h-3" /> : <Copy className="w-3 h-3" />}
            </Button>
          </div>
          <pre className="text-green-400 text-sm overflow-x-auto">
            <code>{message.sql}</code>
          </pre>
        </div>
      )}

      {/* 데이터 뷰 모드 선택 및 버튼 */}
      <div className="flex items-center justify-between mt-2">
        <div className="flex space-x-2">
          <Button
            variant={viewMode === 'table' && hasTable ? 'default' : 'outline'}
            size="sm"
            onClick={() => hasTable && setViewMode('table')}
            className={`h-8 px-3 ${hasTable ? '' : 'opacity-50 cursor-not-allowed bg-gray-200 text-gray-400 border-gray-300'} ${viewMode === 'table' && hasTable ? 'bg-blue-600 text-white' : ''}`}
            disabled={!hasTable}
          >
            <Table className="w-4 h-4 mr-1" />
            표
          </Button>
          <Button
            variant={viewMode === 'chart' && hasChart ? 'default' : 'outline'}
            size="sm"
            onClick={() => hasChart && setViewMode('chart')}
            className={`h-8 px-3 ${hasChart ? '' : 'opacity-50 cursor-not-allowed bg-gray-200 text-gray-400 border-gray-300'} ${viewMode === 'chart' && hasChart ? 'bg-blue-600 text-white' : ''}`}
            disabled={!hasChart}
          >
            <BarChart3 className="w-4 h-4 mr-1" />
            차트
          </Button>
        </div>
        <Button
          variant="outline"
          size="sm"
          onClick={onDownload}
          className={`h-8 px-3 ${hasTable ? '' : 'opacity-50 cursor-not-allowed bg-gray-200 text-gray-400 border-gray-300'}`}
          disabled={!hasTable}
        >
          <Download className="w-4 h-4 mr-1" />
          엑셀
        </Button>
      </div>

      {/* 데이터 뷰 */}
      {hasTable && (
        <div className="bg-white rounded-md border mt-2">
          {viewMode === 'table' ? (
            <DataTable 
              data={message.rows} 
              columns={message.columns}
              rowCount={message.row_count}
            />
          ) : (
            <ChartView 
              data={message.rows} 
              columns={message.columns}
              chartType={message.chart_suggestion || 'bar'}
            />
          )}
        </div>
      )}

      {/* 실행 정보 */}
      <div className="text-xs text-gray-500 flex items-center justify-between mt-2">
        <span>
          {message.row_count}개 행, {message.execution_time.toFixed(2)}초
        </span>
        {message.cached && (
          <span className="bg-green-100 text-green-800 px-2 py-1 rounded">
            캐시됨
          </span>
        )}
      </div>
    </div>
  );
}
