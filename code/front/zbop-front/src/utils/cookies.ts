// Cookie utility functions

export const Cookies = {
  get(name: string): string | null {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) {
      return parts.pop()?.split(';').shift() || null;
    }
    return null;
  },

  set(name: string, value: string, options: {
    expires?: Date | number;
    path?: string;
    domain?: string;
    secure?: boolean;
    sameSite?: 'Strict' | 'Lax' | 'None';
  } = {}): void {
    let cookieString = `${encodeURIComponent(name)}=${encodeURIComponent(value)}`;

    if (options.expires) {
      if (typeof options.expires === 'number') {
        const date = new Date();
        date.setTime(date.getTime() + options.expires * 1000);
        cookieString += `; expires=${date.toUTCString()}`;
      } else {
        cookieString += `; expires=${options.expires.toUTCString()}`;
      }
    }

    cookieString += `; path=${options.path || '/'}`;

    if (options.domain) {
      cookieString += `; domain=${options.domain}`;
    }

    if (options.secure) {
      cookieString += '; secure';
    }

    if (options.sameSite) {
      cookieString += `; samesite=${options.sameSite}`;
    }

    document.cookie = cookieString;
  },

  remove(name: string, options: { path?: string; domain?: string } = {}): void {
    this.set(name, '', {
      ...options,
      expires: new Date(0),
    });
  },
};
