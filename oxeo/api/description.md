The OxEO API allows you to access the latest water related risk data. 🛰️🌊🌐

## Authorisation

Authorisation routes manage user data.

* **Log in** by requesting an auth token via [/auth/token](/docs#/default/login_for_access_token_auth_token_post)
* **Forgot Password** sends a user a password reset token to their email: [/auth/forgot_password](/docs#/default/forgot_password_auth_forgot_password_post)
* **Reset Password** allows a user to reset their password using the token: [/auth/reset_password](/docs#/default/reset_password_auth_reset_password_post)
* **User Data** can be retrieved by GET to [/users/](docs#/default/read_users_users__get)
* **Create User** via POST to[/users/](docs#/default/read_users_users__post)

## AOIs

An "area of interest" (AOI) is a polygonal geometry + static properties.
A required property is a "label" which must be at least one of ["waterbody", "agricultural_area", "basin", "admin_area"].

* **Read** AOIs querying by id, label, geometry, or key-value properties using GET [/aoi/](/docs#/default/get_aoi_aoi__get)
* **Create** AOIs via POST to [/aoi/](/docs#/default/post_aoi_aoi__post)
* **Update** AOIs via POST to [/aoi/update/](/docs#/default/update_aoi_aoi_update__post)
* **Delete** AOIs via POST to [/delete/](/docs#/default/delete_objs_delete__post)

## Events

Events are timestamped key-value properties, measurements, or predictions associated with a single AOI.
A required property is a "label" which must be at least one of ["ndvi", "water_extents", "soil_moisture", "prediction"].

* **Read** Events querying by id, aoi_id, label, or key-value properties using GET [/events/](/docs#/default/get_events_events__get)
* **Create** Events via POST to [/events/](/docs#/default/post_events_events__post)
* **Update** Events via POST to [/events/update/](/docs#/default/update_events_events_update__post)
* **Delete** Events via POST to [/delete/](/docs#/default/delete_objs_delete__post)

## Assets

Assets are real fixed-capital assets which may be exposed to water risk.
Assets have a point geometry and static properties.
A required property is a "label" which must be at least one of ["mine", "power_station"].

* **Read** Assets querying by id, name, label, company_name, geometry, or key-value properties using GET [/assets/](/docs#/default/get_assets_assets__get)
* **Create** Assets via POST to [/assets/](/docs#/default/post_assets_assets__post)
* **Update** Assets via POST to [/assets/update/](/docs#/default/update_assets_assets_update__post)
* **Delete** Assets via POST to [/delete/](/docs#/default/delete_objs_delete__post)

## Companies

Companies are the ultimate owners of Assets.
Multiple companies can own a single asset.
Companies have no geometry or label, only key-value properties.

* **Read** Companies querying by id, name, or key-value properties using GET [/companies/](/docs#/default/get_companies_companies__get)
* **Create** Companies via POST to [/companies/](/docs#/default/post_companies_companies__post)
* **Update** Companies via POST to [/companies/update/](/docs#/default/update_companies_companies_update__post)
* **Delete** Companies via POST to [/delete/](/docs#/default/delete_objs_delete__post)


</br></br>

**Note**: All POST routes apart from password resets require administrator privileges.
