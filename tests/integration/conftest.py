def create_cognito_accounts():
    result = {}
    sm_client = boto3.client('secretsmanager')
    idp_client = boto3.client('cognito-idp')
    # create regular user account
    sm_response = sm_client.get_random_password(ExcludeCharacters='"''`[]{}():;,$/\\<>|=&',
                                                RequireEachIncludedType=True)
    result["regularUserName"] = "regularUser@example.com"
    result["regularUserPassword"] = sm_response["RandomPassword"]
    try:
        idp_client.admin_delete_user(UserPoolId=globalConfig["UserPool"],
                                     Username=result["regularUserName"])
    except idp_client.exceptions.UserNotFoundException:
        print('Regular user haven''t been created previously')
    idp_response = idp_client.admin_create_user(
        UserPoolId=globalConfig["UserPool"],
        Username=result["regularUserName"],
        TemporaryPassword=result["regularUserPassword"],
        MessageAction='SUPPRESS',
        UserAttributes=[{"Name": "name", "Value": result["regularUserName"]}]
    )
    result["regularUserSub"] = idp_response["User"]["Username"]
    idp_client.admin_set_user_password(
        UserPoolId=globalConfig["UserPool"],
        Username=result["regularUserName"],
        Password=result["regularUserPassword"],
        Permanent=True
    )
    # get new user authentication info
    idp_response = idp_client.initiate_auth(
        AuthFlow='USER_PASSWORD_AUTH',
        AuthParameters={
            'USERNAME': result["regularUserName"],
            'PASSWORD': result["regularUserPassword"]
        },
        ClientId=globalConfig["UserPoolClient"],
    )
    result["regularUserIdToken"] = idp_response["AuthenticationResult"]["IdToken"]
    result["regularUserAccessToken"] = idp_response["AuthenticationResult"]["AccessToken"]
    result["regularUserRefreshToken"] = idp_response["AuthenticationResult"]["RefreshToken"]
    # create administrative user account
    sm_response = sm_client.get_random_password(ExcludeCharacters='"''`[]{}():;,$/\\<>|=&',
                                                RequireEachIncludedType=True)
    result["adminUserName"] = "adminUser@example.com"
    result["adminUserPassword"] = sm_response["RandomPassword"]
    try:
        idp_client.admin_delete_user(UserPoolId=globalConfig["UserPool"],
                                     Username=result["adminUserName"])
    except idp_client.exceptions.UserNotFoundException:
        print('Admin user haven''t been created previously')
    idp_response = idp_client.admin_create_user(
        UserPoolId=globalConfig["UserPool"],
        Username=result["adminUserName"],
        TemporaryPassword=result["adminUserPassword"],
        MessageAction='SUPPRESS',
        UserAttributes=[{"Name": "name", "Value": result["adminUserName"]}]
    )
    result["adminUserSub"] = idp_response["User"]["Username"]
    idp_client.admin_set_user_password(
        UserPoolId=globalConfig["UserPool"],
        Username=result["adminUserName"],
        Password=result["adminUserPassword"],
        Permanent=True
    )
    # add administrative user to the admins group
    idp_client.admin_add_user_to_group(UserPoolId=globalConfig["UserPool"],
                                       Username=result["adminUserName"],
                                       GroupName=globalConfig["UserPoolAdminGroupName"])
    # get new admin user authentication info
    idp_response = idp_client.initiate_auth(
        AuthFlow='USER_PASSWORD_AUTH',
        AuthParameters={
            'USERNAME': result["adminUserName"],
            'PASSWORD': result["adminUserPassword"]
        },
        ClientId=globalConfig["UserPoolClient"],
    )
    result["adminUserIdToken"] = idp_response["AuthenticationResult"]["IdToken"]
    result["adminUserAccessToken"] = idp_response["AuthenticationResult"]["AccessToken"]
    result["adminUserRefreshToken"] = idp_response["AuthenticationResult"]["RefreshToken"]
    return result
