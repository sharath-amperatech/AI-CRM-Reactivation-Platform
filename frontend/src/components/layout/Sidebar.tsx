import { NavLink, useLocation } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'
import {
  LayoutDashboard, Users, Zap, CheckSquare, BarChart3,
  Brain, Settings, ChevronLeft, ChevronRight, Zap as ZapIcon,
  Building2, ChevronDown
} from 'lucide-react'
import { useState, useEffect } from 'react'
import { cn } from '@/lib/utils'
import { useAppStore } from '@/store/appStore'
import { fetchApprovals } from '@/lib/api'

const workspaces = ['Acme Corp', 'Beta Startup', 'Gamma Retail']

export default function Sidebar() {
  const { sidebarCollapsed, setSidebarCollapsed, activeWorkspace, setActiveWorkspace } = useAppStore()
  const [workspaceOpen, setWorkspaceOpen] = useState(false)
  const [pendingCount, setPendingCount] = useState<number | null>(null)
  const location = useLocation()

  useEffect(() => {
    fetchApprovals({ page: 1, page_size: 1 })
      .then(({ total }) => setPendingCount(total))
      .catch(() => {})
  }, [])

  const navItems = [
    { path: '/dashboard', label: 'Dashboard', icon: LayoutDashboard },
    { path: '/leads', label: 'Leads', icon: Users },
    { path: '/campaigns', label: 'Campaigns', icon: Zap },
    {
      path: '/approvals',
      label: 'Approval Inbox',
      icon: CheckSquare,
      badge: pendingCount && pendingCount > 0 ? String(pendingCount) : undefined,
    },
    { path: '/analytics', label: 'Analytics', icon: BarChart3 },
    { path: '/quality', label: 'AI Quality', icon: Brain },
    { path: '/settings', label: 'Settings', icon: Settings },
  ]

  return (
    <motion.div
      animate={{ width: sidebarCollapsed ? 64 : 240 }}
      transition={{ duration: 0.2, ease: 'easeInOut' }}
      className="relative flex flex-col h-screen bg-card border-r border-border overflow-hidden shrink-0 z-20"
    >
      {/* Logo */}
      <div className="flex items-center gap-2 px-4 py-4 border-b border-border min-h-[57px]">
        <div className="flex items-center justify-center w-7 h-7 rounded-md bg-primary/20 shrink-0">
          <ZapIcon className="h-4 w-4 text-primary" />
        </div>
        <AnimatePresence>
          {!sidebarCollapsed && (
            <motion.div
              initial={{ opacity: 0, x: -10 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -10 }}
              transition={{ duration: 0.15 }}
              className="flex items-center"
            >
              <span className="font-bold text-sm text-foreground tracking-tight whitespace-nowrap">
                Reactiv<span className="text-primary">IQ</span>
              </span>
            </motion.div>
          )}
        </AnimatePresence>
      </div>

      {/* Workspace Switcher */}
      <div className="px-2 py-2 border-b border-border">
        <button
          onClick={() => setWorkspaceOpen(!workspaceOpen)}
          className={cn(
            "w-full flex items-center gap-2 px-2 py-1.5 rounded-md hover:bg-accent transition-colors text-left",
            sidebarCollapsed && "justify-center"
          )}
        >
          <Building2 className="h-4 w-4 text-muted-foreground shrink-0" />
          <AnimatePresence>
            {!sidebarCollapsed && (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                className="flex items-center justify-between flex-1 min-w-0"
              >
                <span className="text-xs font-medium text-foreground truncate">{activeWorkspace}</span>
                <ChevronDown className={cn("h-3 w-3 text-muted-foreground transition-transform shrink-0", workspaceOpen && "rotate-180")} />
              </motion.div>
            )}
          </AnimatePresence>
        </button>
        <AnimatePresence>
          {workspaceOpen && !sidebarCollapsed && (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: 'auto' }}
              exit={{ opacity: 0, height: 0 }}
              className="mt-1 space-y-0.5"
            >
              {workspaces.map((ws) => (
                <button
                  key={ws}
                  onClick={() => { setActiveWorkspace(ws); setWorkspaceOpen(false) }}
                  className={cn(
                    "w-full text-left px-2 py-1.5 rounded-md text-xs transition-colors",
                    ws === activeWorkspace
                      ? "bg-primary/10 text-primary"
                      : "text-muted-foreground hover:bg-accent hover:text-foreground"
                  )}
                >
                  {ws}
                </button>
              ))}
            </motion.div>
          )}
        </AnimatePresence>
      </div>

      {/* Navigation */}
      <nav className="flex-1 px-2 py-3 space-y-0.5 overflow-y-auto scrollbar-thin">
        {navItems.map(({ path, label, icon: Icon, badge }) => {
          const isActive = location.pathname === path || location.pathname.startsWith(path + '/')
          return (
            <NavLink
              key={path}
              to={path}
              title={sidebarCollapsed ? label : undefined}
              className={cn(
                "flex items-center gap-2.5 px-2 py-2 rounded-md text-sm transition-colors group relative",
                sidebarCollapsed && "justify-center",
                isActive
                  ? "bg-primary/10 text-primary"
                  : "text-muted-foreground hover:bg-accent hover:text-foreground"
              )}
            >
              <Icon className="h-4 w-4 shrink-0" />
              <AnimatePresence>
                {!sidebarCollapsed && (
                  <motion.span
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    exit={{ opacity: 0 }}
                    className="flex-1 whitespace-nowrap text-sm font-medium"
                  >
                    {label}
                  </motion.span>
                )}
              </AnimatePresence>
              {badge && !sidebarCollapsed && (
                <span className="ml-auto text-[10px] font-medium bg-primary/20 text-primary rounded-full px-1.5 py-0.5 leading-none">
                  {badge}
                </span>
              )}
              {badge && sidebarCollapsed && (
                <span className="absolute top-0.5 right-0.5 w-2 h-2 bg-primary rounded-full" />
              )}
            </NavLink>
          )
        })}
      </nav>

      {/* Bottom section */}
      <div className="border-t border-border">
        {/* Demo label */}
        <AnimatePresence>
          {!sidebarCollapsed && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="px-4 py-2"
            >
              <span className="inline-flex items-center gap-1.5 text-[10px] font-medium uppercase tracking-wider text-muted-foreground/60">
                <span className="w-1.5 h-1.5 rounded-full bg-yellow-500/60 inline-block" />
                Demo Mode
              </span>
            </motion.div>
          )}
        </AnimatePresence>

        {/* User info */}
        <div className={cn("flex items-center gap-2 px-3 py-3", sidebarCollapsed && "justify-center px-2")}>
          <div className="w-7 h-7 rounded-full bg-primary/20 flex items-center justify-center shrink-0 text-xs font-bold text-primary">
            S
          </div>
          <AnimatePresence>
            {!sidebarCollapsed && (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                className="flex-1 min-w-0"
              >
                <p className="text-xs font-medium text-foreground truncate">Sharath Kumar</p>
                <p className="text-[10px] text-muted-foreground truncate">sharath.kumar@amperatech.ai</p>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </div>

      {/* Collapse Toggle */}
      <button
        onClick={() => setSidebarCollapsed(!sidebarCollapsed)}
        className="absolute -right-3 top-[72px] w-6 h-6 rounded-full bg-card border border-border flex items-center justify-center hover:bg-accent transition-colors z-10"
      >
        {sidebarCollapsed
          ? <ChevronRight className="h-3 w-3 text-muted-foreground" />
          : <ChevronLeft className="h-3 w-3 text-muted-foreground" />
        }
      </button>
    </motion.div>
  )
}
