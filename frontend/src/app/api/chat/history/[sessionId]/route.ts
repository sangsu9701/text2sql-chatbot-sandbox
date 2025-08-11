import { NextRequest, NextResponse } from 'next/server';

export const dynamic = 'force-dynamic';

const BACKEND_URL = process.env.BACKEND_URL || 'http://localhost:8000';

export async function GET(request: NextRequest, context: { params: Promise<{ sessionId?: string }> }) {
  try {
    const { sessionId } = await context.params;
    if (!sessionId) {
      return NextResponse.json({ error: 'sessionId가 필요합니다.' }, { status: 400 });
    }
    // 백엔드 API 호출
    const response = await fetch(`${BACKEND_URL}/api/v1/chat/history/${sessionId}`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
      // Next dev 환경에서 fetch 캐시로 인해 지연/캐시될 수 있어 no-store 권장
      cache: 'no-store',
    });
    if (!response.ok) {
      throw new Error(`Backend API error: ${response.status}`);
    }
    const data = await response.json();
    return NextResponse.json(data);
  } catch (error) {
    console.error('Chat history API error:', error);
    return NextResponse.json(
      { 
        error: '채팅 기록 조회 중 오류가 발생했습니다.',
        detail: error instanceof Error ? error.message : 'Unknown error'
      },
      { status: 500 }
    );
  }
}

export async function DELETE(request: NextRequest, context: { params: Promise<{ sessionId?: string }> }) {
  try {
    const { sessionId } = await context.params;
    if (!sessionId) {
      return NextResponse.json({ error: 'sessionId가 필요합니다.' }, { status: 400 });
    }
    // 백엔드 API 호출
    const response = await fetch(`${BACKEND_URL}/api/v1/chat/history/${sessionId}`, {
      method: 'DELETE',
      headers: {
        'Content-Type': 'application/json',
      },
      cache: 'no-store',
    });
    if (!response.ok) {
      throw new Error(`Backend API error: ${response.status}`);
    }
    const data = await response.json();
    return NextResponse.json(data);
  } catch (error) {
    console.error('Chat history delete API error:', error);
    return NextResponse.json(
      { 
        error: '채팅 기록 삭제 중 오류가 발생했습니다.',
        detail: error instanceof Error ? error.message : 'Unknown error'
      },
      { status: 500 }
    );
  }
}
