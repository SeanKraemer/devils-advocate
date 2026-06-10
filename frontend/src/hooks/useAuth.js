import { useState, useEffect } from 'react'
import {
    DEMO_MODE,
    auth,
    googleProvider,
    githubProvider,
    signInAnonymously,
    signInWithPopup,
    onAuthStateChanged,
    signOut,
} from '../firebase'

const DEMO_USER = {
    uid: 'demo-user',
    isAnonymous: true,
    displayName: 'Demo user',
    getIdToken: async () => 'demo-token',
}

/**
 * useAuth
 *
 * Handles Firebase auth lifecycle:
 * - Auto signs in anonymously if no user is present
 * - Exposes user, authReady, and sign-in/out actions
 *
 * Returns:
 *   user        - Firebase user object or null
 *   authReady   - true once the initial auth state has resolved
 *   signInWithGoogle
 *   signInWithGitHub
 *   handleSignOut
 */
export function useAuth() {
    const [user, setUser] = useState(DEMO_MODE ? DEMO_USER : null)
    const [authReady, setAuthReady] = useState(DEMO_MODE)

    useEffect(() => {
        if (DEMO_MODE) {
            return undefined
        }
        const unsubscribe = onAuthStateChanged(auth, (firebaseUser) => {
            if (firebaseUser) {
                setUser(firebaseUser)
            } else {
                signInAnonymously(auth)
            }
            setAuthReady(true)
        })
        return () => unsubscribe()
    }, [])

    async function signInWithGoogle() {
        if (DEMO_MODE) return
        try {
            await signInWithPopup(auth, googleProvider)
        } catch (err) {
            console.error('Google sign-in error:', err)
        }
    }

    async function signInWithGitHub() {
        if (DEMO_MODE) return
        try {
            await signInWithPopup(auth, githubProvider)
        } catch (err) {
            console.error('GitHub sign-in error:', err)
        }
    }

    async function handleSignOut() {
        if (DEMO_MODE) return
        await signOut(auth)
        // onAuthStateChanged fires and triggers signInAnonymously again.
    }

    return { user, authReady, signInWithGoogle, signInWithGitHub, handleSignOut }
}
