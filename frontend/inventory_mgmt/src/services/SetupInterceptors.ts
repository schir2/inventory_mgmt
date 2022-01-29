import LocalStorageService from "@/services/LocalStorageService";
import axiosInstance from "@/services/AxiosInstance";
import {Store} from "vuex";
import {config} from "@/config/config";

const setup = (store: Store<any>) => {
    axiosInstance.interceptors.request.use(
        (config) => {
            const token = LocalStorageService.getLocalAccessToken();
            if (token) {
                config.headers!["Authorization"] = "JWT " + token;
            }
            return config;
        },
        (error) => {
            return Promise.reject(error);
        }
    );

    axiosInstance.interceptors.response.use(
        (res) => {
            return res;
        },
        async (err) => {
            const originalConfig = err.config;

            if (originalConfig.url !== "/auth/signin" && err.response) {
                // Access Token was expired
                console.log(err.response.status, originalConfig._retry);
                if (err.response.status === 401 && !originalConfig._retry) {
                    originalConfig._retry = true;

                    try {
                        const rs = await axiosInstance.post(`${config.HOST}/auth/jwt/refresh`, {
                            refresh: LocalStorageService.getLocalRefreshToken(),
                        });

                        const {access} = rs.data;

                        await store.dispatch("auth/refreshToken", access);
                        LocalStorageService.updateLocalAccessToken(access);

                        return axiosInstance(originalConfig);
                    } catch (_error) {
                        return Promise.reject(_error);
                    }
                }
            }
            return Promise.reject(err);
        }
    );
};

export default setup;
