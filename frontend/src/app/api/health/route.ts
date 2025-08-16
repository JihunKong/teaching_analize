import { NextResponse } from 'next/server'

export async function GET() {
  return NextResponse.json(
    {
      status: 'healthy',
      service: 'AIBOA Frontend',
      timestamp: new Date().toISOString(),
      version: '1.0.0',
    },
    { status: 200 }
  )
}