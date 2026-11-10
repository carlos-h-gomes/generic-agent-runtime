# React frontend

This boundary owns presentation, client-side navigation, interaction state, accessibility, and browser-side integrations. It communicates with the Python backend only through the versioned HTTP contract.

`src/App.tsx` and `src/main.tsx` are thin composition roots. HTTP transport belongs in `src/api`; presentation-side orchestration belongs in `src/services`; authoritative business rules remain in the backend.
