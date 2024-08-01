## IR motion detector

Prototype application that takes a stream and detects objects within that stream, comparing the background of the scene to any changes.
The user can define zones that will trigger a udp message signifying whether someone (or something) has entered or left the zone.

Code is a bit messy as just trying a bunch of things out (and it is also being written in Python).

## How it works

A python script runs and spins up a thread that does processing on the stream via OpenCV, and a Flask/Websocket server is also spun up
where the user can change parameters for the stream. The user can navigate to a page in the browser (http://localhost:5000 by default)
where they change these parameters and see the various stages of image processing.

This includes being able to define a zone for detection, the threshold of differences that are detected, image scaling and others.

## Other dependencies

Also uses Tailwind for CSS. Run `npm install` and then `npm run create-css` to update any changes you make to the markup.
