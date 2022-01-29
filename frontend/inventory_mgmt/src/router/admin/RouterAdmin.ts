import customerAdminRoutes from "@/router/admin/RouterAdminCustomer";

const adminRoutes = [{
    path: "/admin",
    name: "admin",
    title: "Admin",
    component: () => import(/* webpackChunkName: "admin" */ "@/views/admin/TheAdmin.vue"),
    children: customerAdminRoutes
}]



export default adminRoutes