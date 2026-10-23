/**
 * Auth Module for هوش افزا
 */
const Auth = (() => {
    function isLoggedIn() {
        return !!API.getToken();
    }

    function isAdmin() {
        const user = API.getUser();
        return !!user && user.role === 'ADMIN';
    }

    function getUser() {
        return API.getUser();
    }

    async function login(phoneNumber, password) {
        const data = await API.login({
            phone_number: phoneNumber,
            password: password,
        });
        API.setToken(data.access_token);
        if (data.refresh_token) {
            API.setRefreshToken(data.refresh_token);
        }
        const user = data.user || null;
        API.setUser(user);
        return user;
    }

    async function register(phoneNumber, password, firstName, lastName) {
        const data = await API.register({
            phone_number: phoneNumber,
            password: password,
            first_name: firstName,
            last_name: lastName,
        });
        API.setToken(data.access_token);
        if (data.refresh_token) {
            API.setRefreshToken(data.refresh_token);
        }
        const user = data.user || null;
        API.setUser(user);
        return user;
    }

    function logout() {
        API.clearTokens();
        API.setUser(null);
        window.location.href = '/';
    }

    async function updateProfile(data) {
        const result = await API.put('/users/me', data);
        API.setUser(result);
        return result;
    }

    return {
        isLoggedIn,
        isAdmin,
        getUser,
        login,
        register,
        logout,
        updateProfile,
    };
})();
