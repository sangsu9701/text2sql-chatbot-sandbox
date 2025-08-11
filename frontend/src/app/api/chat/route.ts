import { NextRequest, NextResponse } from 'next/server';
import { ChatRequest, ChatResponse } from '@/types/chat';

const BACKEND_URL = process.env.BACKEND_URL || 'http://localhost:8000';

export async function POST(request: NextRequest) {
  try {
    const body: ChatRequest = await request.json();
    
    // 백엔드 API 호출
    const response = await fetch(`${BACKEND_URL}/api/v1/chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(body),
    });

    if (!response.ok) {
      throw new Error(`Backend API error: ${response.status}`);
    }

    const data: ChatResponse = await response.json();
    
    return NextResponse.json(data);
  } catch (error) {
    console.error('Chat API error:', error);
    return NextResponse.json(
      { 
        error: '채팅 처리 중 오류가 발생했습니다.',
        detail: error instanceof Error ? error.message : 'Unknown error'
      },
      { status: 500 }
    );
  }
}
