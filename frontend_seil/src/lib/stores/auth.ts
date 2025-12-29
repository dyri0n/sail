import { writable } from 'svelte/store';
import { browser } from '$app/environment';

interface AuthState {
    isAuthenticated: boolean;
    token: string | null;
    user: any | null; // Can be expanded with a proper User interface later
}

const initialState: AuthState = {
    isAuthenticated: false,
    token: null,
    user: null,
};

function createAuthStore() {
    const { subscribe, set, update } = writable<AuthState>(initialState);

    return {
        subscribe,
        initialize: () => {
            if (browser) {
                const token = localStorage.getItem('access_token');
                if (token) {
                    update(state => ({ ...state, isAuthenticated: true, token }));
                }
            }
        },
        setToken: (token: string) => {
            if (browser) {
                localStorage.setItem('access_token', token);
            }
            update(state => ({ ...state, isAuthenticated: true, token }));
        },
        clearToken: () => {
            if (browser) {
                localStorage.removeItem('access_token');
            }
            set(initialState);
        },
        setUser: (user: any) => {
            update(state => ({ ...state, user }));
        }
    };
}

export const auth = createAuthStore();
