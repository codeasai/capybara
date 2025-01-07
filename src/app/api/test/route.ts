import { NextRequest, NextResponse } from 'next/server'

export async function GET() {
  try {
    const healthCheck = await fetch('http://127.0.0.1:8000/api/health', {
      headers: {
        'Accept': 'application/json',
      },
    })
    const result = await healthCheck.json()
    return NextResponse.json({ 
      message: "API is working",
      fastapi_status: result
    })
  } catch (error) {
    return NextResponse.json({ 
      error: 'FastAPI connection failed',
      details: error instanceof Error ? error.message : String(error)
    }, { status: 503 })
  }
}

export async function POST(request: NextRequest) {
  try {
    console.log('Received POST request to /api/test')
    const formData = await request.formData()
    const file = formData.get('file')
    
    if (!file) {
      console.log('No file in request')
      return NextResponse.json({ error: 'No file uploaded' }, { status: 400 })
    }

    console.log('File received:', file instanceof File ? {
      name: file.name,
      type: file.type,
      size: file.size
    } : 'Not a File object')

    try {
      console.log('Testing FastAPI connection...')
      const healthCheck = await fetch('http://127.0.0.1:8000/api/health', {
        headers: {
          'Accept': 'application/json',
        },
      })
      const healthResult = await healthCheck.json()
      console.log('FastAPI health check result:', healthResult)

      const dummyFormData = new FormData()
      dummyFormData.append('file', file)
      
      console.log('Sending test request to FastAPI...')
      const testResponse = await fetch('http://127.0.0.1:8000/api/upload-large-pdf', {
        method: 'POST',
        body: dummyFormData,
      })

      const responseData = await testResponse.text()
      console.log('FastAPI test response:', responseData)

      return NextResponse.json({ 
        message: "Test completed",
        file: {
          name: file instanceof File ? file.name : 'unknown',
          type: file instanceof File ? file.type : 'unknown',
          size: file instanceof File ? file.size : 'unknown'
        },
        fastapi_health: healthResult,
        fastapi_test: responseData
      })

    } catch (error) {
      console.error('FastAPI test error:', error)
      return NextResponse.json({ 
        error: 'FastAPI test failed',
        details: error instanceof Error ? error.message : String(error)
      }, { status: 503 })
    }

  } catch (error) {
    console.error('Test endpoint error:', error)
    return NextResponse.json({ 
      error: 'Test failed',
      details: error instanceof Error ? error.message : String(error)
    }, { status: 500 })
  }
} 