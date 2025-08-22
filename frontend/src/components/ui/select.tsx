'use client'

import * as React from "react"
import { cn } from "@/lib/utils"
import { ChevronDownIcon } from "lucide-react"

interface SelectContextValue {
  value: string
  onValueChange: (value: string) => void
  open: boolean
  setOpen: (open: boolean) => void
}

const SelectContext = React.createContext<SelectContextValue | undefined>(undefined)

const useSelectContext = () => {
  const context = React.useContext(SelectContext)
  if (!context) {
    throw new Error("Select components must be used within a Select component")
  }
  return context
}

export interface SelectProps {
  value: string
  onValueChange: (value: string) => void
  children: React.ReactNode
}

const Select = ({ value, onValueChange, children }: SelectProps) => {
  const [open, setOpen] = React.useState(false)

  return (
    <SelectContext.Provider value={{ value, onValueChange, open, setOpen }}>
      <div className="relative">
        {children}
      </div>
    </SelectContext.Provider>
  )
}

export interface SelectTriggerProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {}

const SelectTrigger = React.forwardRef<HTMLButtonElement, SelectTriggerProps>(
  ({ className, children, ...props }, ref) => {
    const { open, setOpen } = useSelectContext()

    return (
      <button
        ref={ref}
        className={cn(
          "flex h-10 w-full items-center justify-between rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50",
          "border-gray-300 focus:border-blue-500 focus:ring-blue-500",
          className
        )}
        onClick={() => setOpen(!open)}
        {...props}
      >
        {children}
        <ChevronDownIcon className="h-4 w-4 opacity-50" />
      </button>
    )
  }
)
SelectTrigger.displayName = "SelectTrigger"

export interface SelectValueProps extends React.HTMLAttributes<HTMLSpanElement> {
  placeholder?: string
}

const SelectValue = React.forwardRef<HTMLSpanElement, SelectValueProps>(
  ({ className, placeholder, ...props }, ref) => {
    const { value } = useSelectContext()
    const [selectedLabel, setSelectedLabel] = React.useState<string>("")

    // This is a simplified version - in a real implementation, 
    // you'd want to extract the label from the selected item
    React.useEffect(() => {
      setSelectedLabel(value || placeholder || "")
    }, [value, placeholder])

    return (
      <span
        ref={ref}
        className={cn("block truncate", className)}
        {...props}
      >
        {selectedLabel}
      </span>
    )
  }
)
SelectValue.displayName = "SelectValue"

export interface SelectContentProps extends React.HTMLAttributes<HTMLDivElement> {}

const SelectContent = React.forwardRef<HTMLDivElement, SelectContentProps>(
  ({ className, children, ...props }, ref) => {
    const { open, setOpen } = useSelectContext()

    if (!open) return null

    return (
      <>
        {/* Backdrop */}
        <div 
          className="fixed inset-0 z-40" 
          onClick={() => setOpen(false)}
        />
        
        {/* Content */}
        <div
          ref={ref}
          className={cn(
            "absolute top-full left-0 z-50 w-full mt-1 max-h-60 overflow-auto rounded-md border bg-popover p-1 text-popover-foreground shadow-md",
            "bg-white border-gray-200 shadow-lg",
            className
          )}
          {...props}
        >
          {children}
        </div>
      </>
    )
  }
)
SelectContent.displayName = "SelectContent"

export interface SelectItemProps extends React.HTMLAttributes<HTMLDivElement> {
  value: string
}

const SelectItem = React.forwardRef<HTMLDivElement, SelectItemProps>(
  ({ className, value, children, ...props }, ref) => {
    const { value: selectedValue, onValueChange, setOpen } = useSelectContext()
    const isSelected = selectedValue === value

    return (
      <div
        ref={ref}
        className={cn(
          "relative flex w-full cursor-default select-none items-center rounded-sm py-1.5 pl-8 pr-2 text-sm outline-none hover:bg-accent hover:text-accent-foreground focus:bg-accent focus:text-accent-foreground",
          "hover:bg-blue-50 focus:bg-blue-50",
          isSelected && "bg-blue-100 text-blue-900",
          className
        )}
        onClick={() => {
          onValueChange(value)
          setOpen(false)
        }}
        {...props}
      >
        {isSelected && (
          <span className="absolute left-2 flex h-3.5 w-3.5 items-center justify-center">
            ✓
          </span>
        )}
        {children}
      </div>
    )
  }
)
SelectItem.displayName = "SelectItem"

export { Select, SelectTrigger, SelectValue, SelectContent, SelectItem }