"use client";

import { useState, useRef, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { MessageCircle, X, Send, Download, BarChart3, Table, Maximize2, Minimize2, Trash2 } from "lucide-react";
import ChatMessage from "./ChatMessage";
import { ChatRequest, ChatResponse, ChatMessage as ChatMessageType } from "@/types/chat";

interface ChatWidgetProps {
  isOpen: boolean;
  onClose: () => void;
}

export default function ChatWidget({ isOpen, onClose }: ChatWidgetProps) {
  const [messages, setMessages] = useState<ChatMessageType[]>([]);
  const [inputValue, setInputValue] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [isMaximized, setIsMaximized] = useState(false);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  // sessionId를 localStorage에서 관리
  useEffect(() => {
    let sid = localStorage.getItem('akeeon-chat-session');
    if (!sid) {
      sid = 'akeeon-session-' + Math.random().toString(36).slice(2) + '-' + Date.now();
      localStorage.setItem('akeeon-chat-session', sid);
    }
    setSessionId(sid);
  }, []);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    if (isOpen) {
      inputRef.current?.focus();
      // 채팅 기록 로드
      loadChatHistory();
    }
  }, [isOpen]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!inputValue.trim() || isLoading) return;

    const question = inputValue.trim();
    setInputValue("");
    setIsLoading(true);

    // 사용자 메시지 추가
    const userMessage: ChatMessageType = {
      id: Date.now().toString(),
      type: 'user',
      content: question,
      timestamp: new Date()
    };
    setMessages(prev => [...prev, userMessage]);

    try {
      const request: ChatRequest = {
        question,
        wants_visualization: false,
        session_id: sessionId || "demo-session-" + Date.now() // sessionId가 null일 경우 대비
      };

      const response = await fetch("/api/chat", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(request),
      });

      if (!response.ok) {
        throw new Error("API 요청 실패");
      }

      const data: ChatResponse = await response.json();
      
      // AI 메시지 추가
      const aiMessage: ChatMessageType = {
        id: (Date.now() + 1).toString(),
        type: 'ai',
        content: data.answer_text,
        timestamp: new Date(),
        data: data
      };
      setMessages(prev => [...prev, aiMessage]);
    } catch (error) {
      console.error("채팅 오류:", error);
      // 에러 메시지 추가
      const errorMessage: ChatMessageType = {
        id: (Date.now() + 1).toString(),
        type: 'ai',
        content: "죄송합니다. 요청을 처리하는 중 오류가 발생했습니다.",
        timestamp: new Date(),
        data: {
          answer_text: "죄송합니다. 요청을 처리하는 중 오류가 발생했습니다.",
          sql: "",
          rows: [],
          columns: [],
          row_count: 0,
          execution_time: 0,
          cached: false
        }
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleDownload = async (sql: string) => {
    try {
      const response = await fetch("/api/download/xlsx", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ sql, format: "xlsx" }),
      });

      if (!response.ok) {
        throw new Error("다운로드 실패");
      }

      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `snop_data_${new Date().toISOString().slice(0, 10)}.xlsx`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (error) {
      console.error("다운로드 오류:", error);
      alert("다운로드 중 오류가 발생했습니다.");
    }
  };

  const handleClearMessages = async () => {
    try {
      // 백엔드에서 채팅 기록 삭제
      await fetch(`/api/chat/history/${sessionId}`, {
        method: 'DELETE',
      });
      
      // 로컬 상태 초기화
      setMessages([]);
    } catch (error) {
      console.error('채팅 기록 삭제 실패:', error);
      // 로컬에서만 초기화
      setMessages([]);
    }
  };

  const loadChatHistory = async () => {
    if (!sessionId) return; // sessionId가 null이면 기록 로드 안 함
    try {
      const response = await fetch(`/api/chat/history/${sessionId}`);
      if (response.ok) {
        const data = await response.json();
        const historyMessages: ChatMessageType[] = data.messages.map((msg: any) => ({
          id: msg.message_id.toString(),
          type: msg.message_type,
          content: msg.content,
          timestamp: new Date(msg.created_at),
          data: msg.sql_query ? {
            answer_text: msg.content,
            sql: msg.sql_query,
            rows: [],
            columns: [],
            row_count: 0,
            execution_time: msg.execution_time || 0,
            cached: msg.cached || false
          } : undefined
        }));
        setMessages(historyMessages);
      }
    } catch (error) {
      console.error('채팅 기록 로드 실패:', error);
    }
  };

  const toggleMaximize = () => {
    setIsMaximized(!isMaximized);
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-end justify-end p-4">
      <div className={`bg-white rounded-lg shadow-2xl flex flex-col transition-all duration-300 ${
        isMaximized 
          ? 'w-full max-w-4xl h-[80vh]' 
          : 'w-full max-w-md h-[600px]'
      }`}>
        {/* 헤더 */}
        <div className="flex items-center justify-between p-4 border-b">
          <div className="flex items-center space-x-2">
            <MessageCircle className="w-5 h-5 text-blue-600" />
            <h3 className="font-semibold text-gray-900">AKeeON-T 챗봇</h3>
          </div>
          <div className="flex items-center space-x-1">
            <Button
              variant="ghost"
              size="icon"
              onClick={handleClearMessages}
              className="h-8 w-8"
              title="대화 내용 지우기"
            >
              <Trash2 className="w-4 h-4" />
            </Button>
            <Button
              variant="ghost"
              size="icon"
              onClick={toggleMaximize}
              className="h-8 w-8"
              title={isMaximized ? "최소화" : "최대화"}
            >
              {isMaximized ? (
                <Minimize2 className="w-4 h-4" />
              ) : (
                <Maximize2 className="w-4 h-4" />
              )}
            </Button>
            <Button
              variant="ghost"
              size="icon"
              onClick={onClose}
              className="h-8 w-8"
            >
              <X className="w-4 h-4" />
            </Button>
          </div>
        </div>

        {/* 메시지 영역 */}
        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          {messages.length === 0 && (
            <div className="text-center text-gray-500 py-8">
              <MessageCircle className="w-12 h-12 mx-auto mb-4 text-gray-300" />
              <p>자연어로 매출 데이터를 질문해보세요!</p>
              <p className="text-sm mt-2">예: "지난 분기 카테고리별 매출 Top 5"</p>
            </div>
          )}
          
          {messages.map((message) => (
            <div key={message.id} className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}>
              <div className={`max-w-[80%] ${message.type === 'user' ? 'bg-blue-600 text-white' : 'bg-gray-100 text-gray-900'} rounded-lg px-4 py-2`}>
                <p className="text-sm">{message.content}</p>
                {message.type === 'ai' && message.data && (
                  <ChatMessage
                    message={message.data}
                    onDownload={() => handleDownload(message.data!.sql)}
                  />
                )}
              </div>
            </div>
          ))}
          
          {isLoading && (
            <div className="flex items-center space-x-2 text-gray-500">
              <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-600"></div>
              <span>답변을 생성하고 있습니다...</span>
            </div>
          )}
          
          <div ref={messagesEndRef} />
        </div>

        {/* 입력 영역 */}
        <form onSubmit={handleSubmit} className="p-4 border-t">
          <div className="flex space-x-2">
            <input
              ref={inputRef}
              type="text"
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              placeholder="질문을 입력하세요..."
              className="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent text-black placeholder-gray-500"
              disabled={isLoading}
            />
            <Button
              type="submit"
              disabled={isLoading || !inputValue.trim()}
              className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50"
            >
              <Send className="w-4 h-4" />
            </Button>
          </div>
        </form>
      </div>
    </div>
  );
}
