import { useEffect } from 'react'

export function useKeyboardShortcuts(shortcuts) {
  useEffect(() => {
    const handleKeyDown = (event) => {
      const isMac = navigator.platform.toUpperCase().indexOf('MAC') >= 0
      const modifierKey = isMac ? event.metaKey : event.ctrlKey

      shortcuts.forEach(({ key, modifier, action, preventDefault = true }) => {
        let matches = false

        if (modifier === 'cmd' && modifierKey && event.key.toLowerCase() === key.toLowerCase()) {
          matches = true
        } else if (modifier === 'shift' && event.shiftKey && event.key.toLowerCase() === key.toLowerCase()) {
          matches = true
        } else if (!modifier && event.key.toLowerCase() === key.toLowerCase()) {
          matches = true
        }

        if (matches) {
          if (preventDefault) {
            event.preventDefault()
          }
          action(event)
        }
      })
    }

    window.addEventListener('keydown', handleKeyDown)
    return () => window.removeEventListener('keydown', handleKeyDown)
  }, [shortcuts])
}
