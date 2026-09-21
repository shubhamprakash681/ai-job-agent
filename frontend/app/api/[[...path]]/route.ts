import { NextRequest, NextResponse } from 'next/server';

export const dynamic = 'force-dynamic';

const BACKEND_URL =
  process.env.BACKEND_API_URL ||
  process.env.NEXT_PUBLIC_API_URL ||
  'http://localhost:8000';

async function handler(request: NextRequest) {
  const targetUrl = `${BACKEND_URL}${request.nextUrl.pathname}${request.nextUrl.search}`;

  const headers = new Headers();
  request.headers.forEach((value, key) => {
    const k = key.toLowerCase();
    if (!['host', 'connection', 'content-length'].includes(k)) {
      headers.set(key, value);
    }
  });

  const fetchOptions: RequestInit = {
    method: request.method,
    headers,
  };

  if (['POST', 'PUT', 'PATCH'].includes(request.method)) {
    try {
      const body = await request.text();
      if (body) {
        fetchOptions.body = body;
      }
    } catch {
      // no body
    }
  }

  try {
    const response = await fetch(targetUrl, fetchOptions);
    const data = await response.text();

    return new NextResponse(data, {
      status: response.status,
      headers: {
        'content-type': response.headers.get('content-type') || 'application/json',
      },
    });
  } catch (error: any) {
    return NextResponse.json(
      { detail: `Failed to connect to backend server: ${error.message}` },
      { status: 502 }
    );
  }
}

export const GET = handler;
export const POST = handler;
export const PUT = handler;
export const DELETE = handler;
export const PATCH = handler;

