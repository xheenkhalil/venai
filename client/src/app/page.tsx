import Link from "next/link";
import { ArrowRight, Bot, Zap, Shield, BarChart3, Globe } from "lucide-react";

export default function Home() {
  return (
    <div className="min-h-screen bg-[#030712] text-white selection:bg-indigo-500/30 overflow-hidden relative">
      {/* Background Gradients */}
      <div className="absolute top-[-20%] left-[-10%] w-[50%] h-[50%] bg-indigo-600/20 blur-[120px] rounded-full pointer-events-none" />
      <div className="absolute bottom-[-20%] right-[-10%] w-[50%] h-[50%] bg-purple-600/20 blur-[120px] rounded-full pointer-events-none" />
      
      {/* Navbar */}
      <nav className="w-full flex items-center justify-between px-6 py-4 md:px-12 backdrop-blur-sm bg-black/10 fixed top-0 z-50 border-b border-white/5">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 rounded-lg bg-gradient-to-tr from-indigo-500 to-purple-500 flex items-center justify-center">
            <Globe className="w-5 h-5 text-white" />
          </div>
          <span className="text-xl font-bold tracking-tight">VenAI</span>
        </div>
        <div className="flex items-center gap-4">
          <Link href="/sign-in" className="text-sm font-medium text-slate-300 hover:text-white transition-colors">
            Sign In
          </Link>
          <Link href="/dashboard" className="text-sm font-medium bg-white text-black px-4 py-2 rounded-full hover:bg-slate-200 transition-all hover:scale-105 active:scale-95">
            Get Started
          </Link>
        </div>
      </nav>

      {/* Hero Section */}
      <main className="pt-32 pb-16 px-6 md:px-12 max-w-7xl mx-auto flex flex-col items-center justify-center text-center relative z-10 min-h-screen">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-white/5 border border-white/10 text-sm font-medium text-indigo-300 mb-8 animate-fade-in-up">
          <span className="relative flex h-2 w-2">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-indigo-400 opacity-75"></span>
            <span className="relative inline-flex rounded-full h-2 w-2 bg-indigo-500"></span>
          </span>
          Phase 1 Foundation is Live
        </div>
        
        <h1 className="text-5xl md:text-7xl font-bold tracking-tight mb-6 leading-tight max-w-4xl">
          Procurement, fully <br />
          <span className="text-transparent bg-clip-text bg-gradient-to-r from-indigo-400 via-purple-400 to-pink-400">
            autonomous & intelligent.
          </span>
        </h1>
        
        <p className="text-lg md:text-xl text-slate-400 mb-10 max-w-2xl leading-relaxed">
          VenAI negotiates, sources, and secures the best deals globally. Give it a budget and a product, and watch it orchestrate your entire supply chain in minutes.
        </p>
        
        <div className="flex flex-col sm:flex-row gap-4 w-full justify-center">
          <Link href="/dashboard" className="group flex items-center justify-center gap-2 bg-indigo-600 hover:bg-indigo-500 text-white px-8 py-4 rounded-full font-medium text-lg transition-all hover:scale-105 hover:shadow-[0_0_40px_-10px_rgba(79,70,229,0.5)]">
            Start Sourcing Now
            <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
          </Link>
        </div>

        {/* Features Grid */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-32 w-full text-left">
          <div className="p-8 rounded-3xl bg-white/5 border border-white/10 backdrop-blur-md hover:bg-white/10 transition-colors group">
            <div className="w-12 h-12 rounded-2xl bg-indigo-500/20 flex items-center justify-center mb-6 group-hover:scale-110 transition-transform">
              <Bot className="w-6 h-6 text-indigo-400" />
            </div>
            <h3 className="text-xl font-semibold mb-3">AI Agents</h3>
            <p className="text-slate-400 leading-relaxed">
              Our autonomous agents call vendors, scrape the web, and negotiate prices on your behalf.
            </p>
          </div>
          
          <div className="p-8 rounded-3xl bg-white/5 border border-white/10 backdrop-blur-md hover:bg-white/10 transition-colors group">
            <div className="w-12 h-12 rounded-2xl bg-purple-500/20 flex items-center justify-center mb-6 group-hover:scale-110 transition-transform">
              <Zap className="w-6 h-6 text-purple-400" />
            </div>
            <h3 className="text-xl font-semibold mb-3">Lightning Fast</h3>
            <p className="text-slate-400 leading-relaxed">
              What used to take procurement teams weeks is now achieved in just a matter of minutes.
            </p>
          </div>
          
          <div className="p-8 rounded-3xl bg-white/5 border border-white/10 backdrop-blur-md hover:bg-white/10 transition-colors group">
            <div className="w-12 h-12 rounded-2xl bg-pink-500/20 flex items-center justify-center mb-6 group-hover:scale-110 transition-transform">
              <BarChart3 className="w-6 h-6 text-pink-400" />
            </div>
            <h3 className="text-xl font-semibold mb-3">Data Driven</h3>
            <p className="text-slate-400 leading-relaxed">
              Every decision is backed by real-time analytics, guaranteeing the best possible profit margins.
            </p>
          </div>
        </div>
      </main>
    </div>
  );
}
