import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"

export default function Home() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center p-24">
      <div className="z-10 max-w-5xl w-full items-center justify-center font-sans text-sm">
        <h1 className="text-6xl font-bold text-center mb-8 bg-gradient-to-r from-primary-600 to-primary-500 bg-clip-text text-transparent">
          Sichelgaita.AI
        </h1>
        <p className="text-2xl text-center text-neutral-600 mb-12">
          Data Wealth Platform
        </p>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 max-w-4xl mx-auto">
          <Card>
            <CardHeader>
              <CardTitle>📊 Data Processing</CardTitle>
              <CardDescription>
                Upload and process Excel, CSV, and PDF files with advanced data analysis tools.
              </CardDescription>
            </CardHeader>
          </Card>
          <Card>
            <CardHeader>
              <CardTitle>🤖 AI Insights</CardTitle>
              <CardDescription>
                Generate intelligent insights powered by Google Gemini Pro AI.
              </CardDescription>
            </CardHeader>
          </Card>
          <Card>
            <CardHeader>
              <CardTitle>📈 Visualizations</CardTitle>
              <CardDescription>
                Beautiful, interactive charts and graphs to understand your data.
              </CardDescription>
            </CardHeader>
          </Card>
          <Card>
            <CardHeader>
              <CardTitle>☁️ Cloud Storage</CardTitle>
              <CardDescription>
                Secure data storage and management with Supabase.
              </CardDescription>
            </CardHeader>
          </Card>
        </div>
        <div className="text-center mt-12">
          <Button size="lg">Get Started</Button>
        </div>
        <div className="text-center mt-8">
          <p className="text-neutral-500">
            🚀 Development server running. Start building amazing features!
          </p>
        </div>
      </div>
    </main>
  );
}
