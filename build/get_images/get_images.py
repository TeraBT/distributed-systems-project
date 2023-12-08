def handler(event, context):
    print(event)
    return {"message": f"Hello from {__file__}"}
