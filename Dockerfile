FROM python:2-onbuild
ADD spaceapi.py /spaceapi.py
ADD space.cfg /space.cfg
CMD [ "python", "./spaceapi.py" ]

