# yakumo
yakumo is a steganography tool. yakumo can save secret data into given photo directory.

### Requirements
* macOS
* Python3
* PNG images

### Usage
**install**
```bash
pip3 install git+https://github.com/TakutoYoshikai/yakumo.git
```

**hide data**
```bash
yakumo hide -i <IMAGE DIR> -d <SECRET DATA DIR>
```

**reveal**
```bash
yakumo reveal -i <IMAGE DIR>
```


### License
MIT License
