import { initializeApp } from 'firebase/app'
import { getAuth, signInAnonymously, signInWithPopup, GoogleAuthProvider, GithubAuthProvider, onAuthStateChanged, signOut } from 'firebase/auth'
import { getStorage, ref, uploadBytesResumable, deleteObject, listAll, getMetadata, getDownloadURL } from 'firebase/storage'

export const DEMO_MODE = import.meta.env.VITE_DEMO_MODE === '1'

const firebaseConfig = {
    apiKey: import.meta.env.VITE_FIREBASE_API_KEY || (DEMO_MODE ? 'demo-api-key' : undefined),
    authDomain: import.meta.env.VITE_FIREBASE_AUTH_DOMAIN || (DEMO_MODE ? 'demo.firebaseapp.com' : undefined),
    projectId: import.meta.env.VITE_FIREBASE_PROJECT_ID || (DEMO_MODE ? 'demo-devils-advocate' : undefined),
    storageBucket: import.meta.env.VITE_FIREBASE_STORAGE_BUCKET || (DEMO_MODE ? 'demo-devils-advocate.firebasestorage.app' : undefined),
    messagingSenderId: import.meta.env.VITE_FIREBASE_MESSAGING_SENDER_ID || (DEMO_MODE ? '000000000000' : undefined),
    appId: import.meta.env.VITE_FIREBASE_APP_ID || (DEMO_MODE ? 'demo-app-id' : undefined),
    measurementId: import.meta.env.VITE_FIREBASE_MEASUREMENT_ID,
}

const app = initializeApp(firebaseConfig)

export const auth = getAuth(app)
export const storage = getStorage(app)
export let analytics = null

if (typeof window !== 'undefined' && firebaseConfig.measurementId) {
    import('firebase/analytics')
        .then(async ({ getAnalytics, isSupported }) => {
            if (await isSupported()) {
                analytics = getAnalytics(app)
            }
        })
        .catch((err) => {
            console.warn('Firebase Analytics unavailable in this environment:', err)
        })
}
export const googleProvider = new GoogleAuthProvider()
export const githubProvider = new GithubAuthProvider()
export { ref, uploadBytesResumable, deleteObject, listAll, getMetadata }

export { signInAnonymously, signInWithPopup, onAuthStateChanged, signOut }
export { getDownloadURL }
