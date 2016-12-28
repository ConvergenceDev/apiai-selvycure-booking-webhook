# Api.ai booking webhook implementation in Python

This is a really simple webhook implementation that gets Api.ai classification JSON (i.e. a JSON output of Api.ai /query endpoint) and returns a fulfillment response.

More info about Api.ai webhooks could be found here:
[Api.ai Webhook](https://docs.api.ai/docs/webhook)

# What does the service do?
After receiving the message, it sends a reservation announcement message to Facebook Messenger to remind the reservation status.