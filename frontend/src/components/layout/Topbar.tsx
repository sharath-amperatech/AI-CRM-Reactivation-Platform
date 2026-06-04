import { useLocation, useNavigate } from 'react-router-dom'
import { Bell, Search, ChevronRight, HelpCircle, ChevronDown, LogOut, User, KeyRound, Sun, Moon } from 'lucide-react'
import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { cn } from '@/lib/utils'
import { useAppStore } from '@/store/appStore'

const routeLabels: Record<string, string> = {
  dashboard: 'Dashboard',
  leads: 'Dormant Leads',
  campaigns: 'Campaigns',
  approvals: 'Approval Inbox',
  analytics: 'Analytics',
  quality: 'AI Quality',
  settings: 'Settings',
  new: 'New Campaign',
}

function getBreadcrumbs(pathname: string) {
  const parts = pathname.split('/').filter(Boolean)
  const crumbs: { label: string; path: string }[] = [{ label: 'ReactivIQ', path: '/' }]
  let acc = ''
  for (const part of parts) {
    acc += `/${part}`
    const label = routeLabels[part] || (part.startsWith('lead-') ? 'Lead Detail' : part.startsWith('campaign-') ? 'Campaign Detail' : part)
    crumbs.push({ label, path: acc })
  }
  return crumbs
}

export default function Topbar() {
  const location = useLocation()
  const navigate = useNavigate()
  const { notificationCount, theme, toggleTheme } = useAppStore()
  const [searchOpen, setSearchOpen] = useState(false)
  const [searchValue, setSearchValue] = useState('')
  const [userMenuOpen, setUserMenuOpen] = useState(false)
  const [notifOpen, setNotifOpen] = useState(false)

  const breadcrumbs = getBreadcrumbs(location.pathname)

  useEffect(() => {
    const handler = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
        e.preventDefault()
        setSearchOpen(true)
      }
      if (e.key === 'Escape') {
        setSearchOpen(false)
        setUserMenuOpen(false)
        setNotifOpen(false)
      }
    }
    window.addEventListener('keydown', handler)
    return () => window.removeEventListener('keydown', handler)
  }, [])

  return (
    <div className="h-14 border-b border-border bg-card flex items-center justify-between px-4 gap-4 shrink-0 z-10">
      {/* Breadcrumb */}
      <div className="flex items-center gap-1.5 min-w-0">
        {breadcrumbs.map((crumb, i) => (
          <div key={crumb.path} className="flex items-center gap-1.5 min-w-0">
            {i > 0 && <ChevronRight className="h-3.5 w-3.5 text-muted-foreground/50 shrink-0" />}
            <button
              onClick={() => navigate(crumb.path)}
              className={cn(
                "text-sm truncate transition-colors",
                i === breadcrumbs.length - 1
                  ? "text-foreground font-medium"
                  : "text-muted-foreground hover:text-foreground"
              )}
            >
              {crumb.label}
            </button>
          </div>
        ))}
      </div>

      {/* Right side controls */}
      <div className="flex items-center gap-2 shrink-0">
        {/* Search */}
        <button
          onClick={() => setSearchOpen(true)}
          className="flex items-center gap-2 px-3 h-8 rounded-md bg-muted/50 border border-border text-muted-foreground text-xs hover:bg-muted transition-colors"
        >
          <Search className="h-3.5 w-3.5" />
          <span className="hidden sm:block">Search...</span>
          <kbd className="hidden sm:inline-flex items-center gap-0.5 text-[10px] bg-background rounded px-1 py-0.5 border border-border font-medium">
            ⌘K
          </kbd>
        </button>

        {/* AI Activity */}
        <div className="hidden md:flex items-center gap-1.5 px-2.5 py-1 rounded-md bg-green-500/10 border border-green-500/20">
          <motion.div
            animate={{ scale: [1, 1.3, 1] }}
            transition={{ repeat: Infinity, duration: 2 }}
            className="w-1.5 h-1.5 rounded-full bg-green-500"
          />
          <span className="text-[10px] font-medium text-green-400">AI Running</span>
        </div>

        {/* Demo badge */}
        <span className="hidden md:inline-flex items-center gap-1 text-[10px] font-medium text-muted-foreground/60 bg-muted/50 border border-border/50 rounded px-1.5 py-0.5">
          <span className="w-1 h-1 rounded-full bg-yellow-500/60" />
          Demo Data
        </span>

        {/* Help */}
        <button className="w-8 h-8 rounded-md flex items-center justify-center text-muted-foreground hover:bg-accent transition-colors">
          <HelpCircle className="h-4 w-4" />
        </button>

        {/* Theme toggle */}
        <button
          onClick={toggleTheme}
          title={theme === 'dark' ? 'Switch to light mode' : 'Switch to dark mode'}
          className="w-8 h-8 rounded-md flex items-center justify-center text-muted-foreground hover:bg-accent transition-colors"
        >
          {theme === 'dark' ? <Sun className="h-4 w-4" /> : <Moon className="h-4 w-4" />}
        </button>

        {/* Notifications */}
        <div className="relative">
          <button
            onClick={() => setNotifOpen(!notifOpen)}
            className="relative w-8 h-8 rounded-md flex items-center justify-center text-muted-foreground hover:bg-accent transition-colors"
          >
            <Bell className="h-4 w-4" />
            {notificationCount > 0 && (
              <span className="absolute -top-0.5 -right-0.5 w-4 h-4 bg-primary rounded-full text-[9px] font-bold text-primary-foreground flex items-center justify-center">
                {notificationCount}
              </span>
            )}
          </button>
          {notifOpen && (
            <div className="absolute right-0 top-full mt-1 w-72 bg-card border border-border rounded-lg shadow-xl z-50">
              <div className="p-3 border-b border-border">
                <p className="text-xs font-semibold text-foreground">Notifications</p>
              </div>
              <div className="divide-y divide-border">
                {[
                  { text: '12 approvals waiting for review', time: '5m ago', type: 'approval' },
                  { text: 'Campaign 001 — 68.4% open rate reached', time: '1h ago', type: 'campaign' },
                  { text: 'AI Quality alert: faithfulness dipped below 0.85', time: '3h ago', type: 'alert' },
                  { text: 'HubSpot sync completed — 147 new activities', time: '5h ago', type: 'sync' },
                ].map((n, i) => (
                  <div key={i} className="px-3 py-2.5 hover:bg-muted/30 transition-colors cursor-pointer">
                    <p className="text-xs text-foreground">{n.text}</p>
                    <p className="text-[10px] text-muted-foreground mt-0.5">{n.time}</p>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* User Menu */}
        <div className="relative">
          <button
            onClick={() => setUserMenuOpen(!userMenuOpen)}
            className="flex items-center gap-1.5 hover:bg-accent rounded-md px-1.5 py-1 transition-colors"
          >
            <div className="w-6 h-6 rounded-full bg-primary/20 flex items-center justify-center text-[10px] font-bold text-primary">
              S
            </div>
            <ChevronDown className="h-3 w-3 text-muted-foreground" />
          </button>
          {userMenuOpen && (
            <div className="absolute right-0 top-full mt-1 w-48 bg-card border border-border rounded-lg shadow-xl z-50">
              <div className="p-2.5 border-b border-border">
                <p className="text-xs font-medium text-foreground">Sharath Kumar</p>
                <p className="text-[10px] text-muted-foreground">sharath.kumar@amperatech.ai</p>
              </div>
              <div className="p-1">
                <button className="w-full flex items-center gap-2 px-2 py-1.5 rounded text-xs text-muted-foreground hover:bg-accent hover:text-foreground transition-colors">
                  <User className="h-3.5 w-3.5" /> Profile
                </button>
                <button className="w-full flex items-center gap-2 px-2 py-1.5 rounded text-xs text-muted-foreground hover:bg-accent hover:text-foreground transition-colors" onClick={() => { navigate('/settings'); setUserMenuOpen(false) }}>
                  <KeyRound className="h-3.5 w-3.5" /> API Keys
                </button>
                <button className="w-full flex items-center gap-2 px-2 py-1.5 rounded text-xs text-red-400 hover:bg-red-500/10 transition-colors">
                  <LogOut className="h-3.5 w-3.5" /> Sign Out
                </button>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Global Search Modal */}
      {searchOpen && (
        <div className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-start justify-center pt-24" onClick={() => setSearchOpen(false)}>
          <div className="w-full max-w-lg bg-card border border-border rounded-xl shadow-2xl" onClick={e => e.stopPropagation()}>
            <div className="flex items-center gap-2 px-4 py-3 border-b border-border">
              <Search className="h-4 w-4 text-muted-foreground" />
              <input
                autoFocus
                value={searchValue}
                onChange={e => setSearchValue(e.target.value)}
                placeholder="Search leads, campaigns, approvals..."
                className="flex-1 bg-transparent text-sm text-foreground placeholder:text-muted-foreground outline-none"
              />
              <kbd className="text-[10px] bg-muted rounded px-1.5 py-0.5 text-muted-foreground border border-border">ESC</kbd>
            </div>
            <div className="p-2">
              {['Sarah Chen — TechFlow Solutions', 'Q2 Pricing Objection Revival', 'Approval: Marcus Williams', 'DataSphere Analytics — Natasha Ivanova'].map((item, i) => (
                <button key={i} className="w-full text-left px-3 py-2 rounded text-sm text-muted-foreground hover:bg-accent hover:text-foreground transition-colors">
                  {item}
                </button>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
