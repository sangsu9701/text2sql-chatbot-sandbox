"use client";

import { useState } from "react";
import ChatWidget from "@/components/ChatWidget";
import { Button } from "@/components/ui/button";
import { MessageCircle, X } from "lucide-react";

export default function Home() {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 p-4">
      <div className="max-w-4xl mx-auto">
        <div className="text-center py-12">
          <h1 className="text-4xl font-bold text-gray-900 mb-4">
            AKeeON-T
          </h1>
          <p className="text-xl text-gray-600 mb-8">
            SNoP 매출 데이터 Text-to-SQL 임베더블 챗봇
          </p>
          <p className="text-gray-500 mb-8">
            자연어 질문을 SQL로 변환해 매출 데이터를 분석해보세요
          </p>
          
          <div className="space-y-4">
            <Button 
              onClick={() => setIsOpen(true)}
              className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-3 rounded-lg"
            >
              <MessageCircle className="w-5 h-5 mr-2" />
              챗봇 시작하기
            </Button>
            
            <div className="text-sm text-gray-400">
              예시 질문: "지난 분기 카테고리별 매출 Top 5 보여줘"
            </div>
          </div>
        </div>

        {/* 기능 소개 */}
        <div className="grid md:grid-cols-3 gap-6 mt-12">
          <div className="bg-white p-6 rounded-lg shadow-sm">
            <h3 className="font-semibold text-lg mb-2">자연어 → SQL</h3>
            <p className="text-gray-600">
              한국어 질문을 정확한 SQL 쿼리로 자동 변환
            </p>
          </div>
          <div className="bg-white p-6 rounded-lg shadow-sm">
            <h3 className="font-semibold text-lg mb-2">데이터 시각화</h3>
            <p className="text-gray-600">
              차트, 그래프, 표로 결과를 직관적으로 표시
            </p>
          </div>
          <div className="bg-white p-6 rounded-lg shadow-sm">
            <h3 className="font-semibold text-lg mb-2">엑셀 다운로드</h3>
            <p className="text-gray-600">
              분석 결과를 XLSX 형태로 다운로드
            </p>
          </div>
        </div>
      </div>

      {/* 챗봇 위젯 */}
      <ChatWidget isOpen={isOpen} onClose={() => setIsOpen(false)} />
    </div>
  );
}
