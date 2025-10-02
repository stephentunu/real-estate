import * as React from "react"

import type {
  ToastActionElement,
  ToastProps,
} from "@/components/ui/toast"

const TOAST_LIMIT = 1
const TOAST_REMOVE_DELAY = 1000000

type ToasterToast = ToastProps & {
  id: string
  title?: React.ReactNode
  description?: React.ReactNode
  action?: ToastActionElement
}

const actionTypes = {
  ADD_TOAST: "ADD_TOAST",
  UPDATE_TOAST: "UPDATE_TOAST",
  DISMISS_TOAST: "DISMISS_TOAST",
  REMOVE_TOAST: "REMOVE_TOAST",
} as const

let count = 0

function genId() {
  count = (count + 1) % Number.MAX_SAFE_INTEGER
  return count.toString()
}

type ActionType = typeof actionTypes

type Action =
  | {
      type: ActionType["ADD_TOAST"]
      toast: ToasterToast
    }
  | {
      type: ActionType["UPDATE_TOAST"]
      toast: Partial<ToasterToast>
    }
  | {
      type: ActionType["DISMISS_TOAST"]
      toastId?: ToasterToast["id"]
    }
  | {
      type: ActionType["REMOVE_TOAST"]
      toastId?: ToasterToast["id"]
    }

interface State {
  toasts: ToasterToast[]
}

const toastTimeouts = new Map<string, ReturnType<typeof setTimeout>>()

const addToRemoveQueue = (toastId: string) => {
  if (toastTimeouts.has(toastId)) {
    return
  }

  const timeout = setTimeout(() => {
    toastTimeouts.delete(toastId)
    dispatch({
      type: "REMOVE_TOAST",
      toastId: toastId,
    })
  }, TOAST_REMOVE_DELAY)

  toastTimeouts.set(toastId, timeout)
}

export const reducer = (state: State, action: Action): State => {
  switch (action.type) {
    case "ADD_TOAST":
      return {
        ...state,
        toasts: [action.toast, ...state.toasts].slice(0, TOAST_LIMIT),
      }

    case "UPDATE_TOAST":
      return {
        ...state,
        toasts: state.toasts.map((t) =>
          t.id === action.toast.id ? { ...t, ...action.toast } : t
        ),
      }

    case "DISMISS_TOAST": {
      const { toastId } = action

      // ! Side effects ! - This could be extracted into a dismissToast() action,
      // but I'll keep it here for simplicity
      if (toastId) {
        addToRemoveQueue(toastId)
      } else {
        state.toasts.forEach((toast) => {
          addToRemoveQueue(toast.id)
        })
      }

      return {
        ...state,
        toasts: state.toasts.map((t) =>
          t.id === toastId || toastId === undefined
            ? {
                ...t,
                open: false,
              }
            : t
        ),
      }
    }
    case "REMOVE_TOAST":
      if (action.toastId === undefined) {
        return {
          ...state,
          toasts: [],
        }
      }
      return {
        ...state,
        toasts: state.toasts.filter((t) => t.id !== action.toastId),
      }
  }
}

const listeners: Array<(state: State) => void> = []

let memoryState: State = { toasts: [] }

function dispatch(action: Action) {
  memoryState = reducer(memoryState, action)
  listeners.forEach((listener) => {
    listener(memoryState)
  })
}

type Toast = Omit<ToasterToast, "id">

function toast({ ...props }: Toast) {
  const id = genId()

  const update = (props: ToasterToast) =>
    dispatch({
      type: "UPDATE_TOAST",
      toast: { ...props, id },
    })
  const dismiss = () => dispatch({ type: "DISMISS_TOAST", toastId: id })

  dispatch({
    type: "ADD_TOAST",
    toast: {
      ...props,
      id,
      open: true,
      onOpenChange: (open) => {
        if (!open) dismiss()
      },
    },
  })

  return {
    id: id,
    dismiss,
    update,
  }
}

function useToast() {
  const [state, setState] = React.useState<State>(memoryState)

  React.useEffect(() => {
    listeners.push(setState)
    return () => {
      const index = listeners.indexOf(setState)
      if (index > -1) {
        listeners.splice(index, 1)
      }
    }
  }, [state])

  return {
    ...state,
    toast,
    dismiss: (toastId?: string) => dispatch({ type: "DISMISS_TOAST", toastId }),
  }
}

// Enhanced toast functions for better error handling
const toastError = (title: string, description?: string) => {
  return toast({
    title,
    description,
    variant: "destructive",
  })
}

const toastSuccess = (title: string, description?: string) => {
  return toast({
    title,
    description,
    variant: "success",
  })
}

const toastWarning = (title: string, description?: string) => {
  return toast({
    title,
    description,
    variant: "warning",
  })
}

const toastInfo = (title: string, description?: string) => {
  return toast({
    title,
    description,
    variant: "default",
  })
}

// API Error handling toast
interface APIError {
  response?: {
    status: number;
    data?: {
      detail?: string;
      message?: string;
    };
  };
  message?: string;
  code?: string;
}

const toastAPIError = (error: APIError | Error | unknown, context?: string) => {
  let title = "Error"
  let description = "An unexpected error occurred"

  // Type guard to check if error has response property
  const hasResponse = (err: unknown): err is APIError => {
    return typeof err === 'object' && err !== null && 'response' in err;
  };

  // Type guard to check if error has message property
  const hasMessage = (err: unknown): err is { message: string } => {
    return typeof err === 'object' && err !== null && 'message' in err && typeof (err as { message: unknown }).message === 'string';
  };

  // Type guard to check if error has code property
  const hasCode = (err: unknown): err is { code: string } => {
    return typeof err === 'object' && err !== null && 'code' in err && typeof (err as { code: unknown }).code === 'string';
  };

  if (hasResponse(error) && error.response?.status) {
    switch (error.response.status) {
      case 400:
        title = "Invalid Request"
        description = error.response.data?.detail || error.response.data?.message || "Please check your input and try again"
        break
      case 401:
        title = "Authentication Required"
        description = "Please log in to continue"
        break
      case 403:
        title = "Access Denied"
        description = "You don't have permission to perform this action"
        break
      case 404:
        title = "Not Found"
        description = "The requested resource was not found"
        break
      case 429:
        title = "Too Many Requests"
        description = "Please wait a moment before trying again"
        break
      case 500:
        title = "Server Error"
        description = "Something went wrong on our end. Please try again later"
        break
      default:
        title = `Error ${error.response.status}`
        description = error.response.data?.detail || error.response.data?.message || "An unexpected error occurred"
    }
  } else if (hasMessage(error)) {
    const errorMessage = error.message.toLowerCase()
    
    // Handle specific connection errors with more user-friendly messages
    if (errorMessage.includes('connection refused') || 
        errorMessage.includes('net::err_connection_refused') ||
        (hasCode(error) && error.code === 'ERR_CONNECTION_REFUSED')) {
      title = "Server Unavailable"
      description = "The server is currently unavailable. Please check if the backend service is running or try again later."
    } else if (errorMessage.includes('network error') || 
               errorMessage.includes('failed to fetch') ||
               errorMessage.includes('fetch')) {
      title = "Connection Error"
      description = "Unable to connect to the server. Please check your internet connection and try again."
    } else if (errorMessage.includes('connection timed out') || 
               errorMessage.includes('etimedout')) {
      title = "Connection Timeout"
      description = "The request took too long to complete. Please check your internet connection and try again."
    } else if (errorMessage.includes('name not resolved') || 
               errorMessage.includes('enotfound')) {
      title = "Server Not Found"
      description = "Unable to find the server. Please check the server address and your internet connection."
    } else {
      description = error.message
    }
  }

  if (context) {
    description = `${description} (${context})`
  }

  return toastError(title, description)
}

// Network status toasts
const toastNetworkOffline = () => {
  return toastWarning(
    "You're Offline",
    "Please check your internet connection"
  )
}

const toastNetworkOnline = () => {
  return toastSuccess(
    "Back Online",
    "Your connection has been restored"
  )
}

export { 
  useToast, 
  toast,
  toastError,
  toastSuccess,
  toastWarning,
  toastInfo,
  toastAPIError,
  toastNetworkOffline,
  toastNetworkOnline
}
