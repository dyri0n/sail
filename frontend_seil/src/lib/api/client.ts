import { PUBLIC_API_BASE_URL } from '$env/static/public';

type HttpMethod = 'GET' | 'POST' | 'PUT' | 'PATCH' | 'DELETE';

interface RequestOptions extends RequestInit {
    method?: HttpMethod;
    body?: any;
}

const getAuthToken = (): string | null => {
    if (typeof window !== 'undefined') {
        return localStorage.getItem('access_token');
    }
    return null;
};

export async function apiRequest<T>(endpoint: string, options: RequestOptions = {}, manualToken?: string): Promise<T> {
    const token = manualToken || getAuthToken();
    const url = `${PUBLIC_API_BASE_URL}${endpoint}`;

    const headers = new Headers(options.headers);

    if (options.body) {
        headers.set('Content-Type', 'application/json');
    }

    if (token) {
        headers.set('Authorization', `Bearer ${token}`);
        console.log(`[API] Using token: ${token.substring(0, 10)}...`);
    } else {
        console.warn(`[API] NO TOKEN PROVIDED for ${endpoint}`);
    }

    console.log(`[API] Sending ${options.method || 'GET'} to ${url}`);
    if (options.body) console.log(`[API] Body:`, JSON.stringify(options.body));

    const response = await fetch(url, {
        ...options,
        headers,
        body: options.body ? JSON.stringify(options.body) : undefined,
    });

    if (!response.ok) {
        let errorData;
        try {
            errorData = await response.json();
        } catch {
            errorData = { message: 'Unknown error' };
        }
        console.error(`[API] Error from ${url}:`, response.status, errorData);
        throw new Error(errorData.detail || errorData.message || `Request failed with status ${response.status}`);
    }

    console.log(`[API] Success from ${url}:`, response.status);

    // Handle empty responses
    if (response.status === 204) {
        return {} as T;
    }

    return await response.json() as T;
}
