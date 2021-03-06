# Data Features

### Face and Eye image

1. landmark 검출 후 얼굴, 왼쪽 눈, 오른쪽 눈 각각 crop
    - landmark 검출 시 pre-trained model([shape_predictor_68_face_landmarks.dat](http://dlib.net/files/shape_predictor_68_face_landmarks.dat.bz2)) 사용
2. Face는 (154, 154, 3) Eye는 (224, 224, 3)로 resize 후 jpg파일로 저장

<img src="https://user-images.githubusercontent.com/43233184/91655583-9c149f00-eaec-11ea-9b8d-50f469c647b9.png" width="550px">

### Headpose

1. 원리
<img src="https://user-images.githubusercontent.com/43233184/91655590-aa62bb00-eaec-11ea-8a0e-faec947e75e6.png" width="500">
<img src="https://user-images.githubusercontent.com/43233184/91655593-afc00580-eaec-11ea-945d-54e9f4f5ff21.png" width="300">
<img src="https://user-images.githubusercontent.com/43233184/91655597-b2225f80-eaec-11ea-9732-5df31ee66176.png" width="300">


- 우리가 알고 있는 좌표인 World coordination, Image plane coordination, Camera coordination을 이용해 Rotation value 검출하는 원리를 이용

2. 값 추출

- [github open api](https://github.com/qhan1028/Headpose-Detection) 이용해 Rotation value인 pitch-yaw-roll(Euler angles) 값 추출


<img src="https://user-images.githubusercontent.com/43233184/91655601-b9e20400-eaec-11ea-80ae-e31bef55f7ee.png" width="300">

# Exploratory Data Analysis

### Dataframe Structure

```
<class 'pandas.core.frame.DataFrame'>
RangeIndex: 13563 entries, 0 to 13562
Data columns (total 10 columns):
 #   Column            Non-Null Count  Dtype  
---  ------            --------------  -----  
 0   frame_name        13563 non-null  object 
 1   subject           13563 non-null  object 
 2   head_pose_pitch   13563 non-null  float64
 3   head_pose_yaw     13563 non-null  float64
 4   head_pose_roll    13563 non-null  float64
 5   face_landmarks    13563 non-null  object 
 6   faceimg_name      13563 non-null  object 
 7   lefteyeimg_name   13563 non-null  object 
 8   righteyeimg_name  13563 non-null  object 
 9   label             13563 non-null  object 
dtypes: float64(3), object(7)
memory usage: 1.0+ MB
```

### Number of data per Subject

<p align="center"><img src="https://user-images.githubusercontent.com/61040406/91696345-659d5980-ebaa-11ea-9571-a0e8becf32ad.png"></p>

### Number of data per Label
<p align="center"><img src="https://user-images.githubusercontent.com/43233184/91655612-c23a3f00-eaec-11ea-9331-f461c35870ff.png"></p>

- label 0(41.92%) : 온라인 수업 **화면이 아닌 곳을 응시**
- label 1(58.08%) : 온라인 수업 **화면 응시**

### Headpose Distribution

#### 2D Density
<p align="center"><img src="https://user-images.githubusercontent.com/61040406/91936097-2433b800-ed2a-11ea-9c12-ffef736e5dc1.png" width="90%"></p>

#### Heatmap (correlation)
<p align="center"><img src="https://user-images.githubusercontent.com/61040406/91936544-0581f100-ed2b-11ea-8093-bae09ef771b7.png", width="50%"></p>

#### Boxplot
<p align="center"><img src="https://user-images.githubusercontent.com/61040406/91696089-0e978480-ebaa-11ea-9d3d-23a77a59e572.png" width="90%"></p>

화면을 보지않는 그룹(label0)과 화면을 보는 그룹(label1)간의 Headpose 차이 

- 두 그룹 간에 pitch, yaw, roll 값이 차이가 있는지 살펴보기 위해 boxplot을 그림
- pitch와 yaw는 두 그룹 사이에 차이가 있는 것으로 보임
- roll은 두 그룹 사이에 차이가 없는 것으로 보임

# Make metadata

## Installing

Install and update using pip:

```python
# opencv
$ pip install opencv-python

# dlib - Before you install dlib, you should install visual studio for c++.
$ pip install cmake
$ pip install dlib 
```

## Repository

```
└── preprocessing
        ├── cut_eyelm.py
        ├── cut_facelm.py
        ├── generate_data.py
        ├── headpose.py
        ├── timer.py
        ├── utils.py
└── EDA.ipynb
```

1. preprocessing
    - 데이터 전처리 및 데이터 저장을 위한 json 파일 생성 폴더
2. EDA.ipynb
    - EDA 및 유의성 검정

## Run

### before run

```python
# generate_data.py

20    video_dir = 'C:/Users/sodaus/Desktop/data/ver3456final/video/' #path of video dir

26    img_dir = 'C:/Users/sodaus/Desktop/data/ver3456final/img/'

126   # metadata 저장을 위한 json 파일 생성 
127   datadict = {}
128   datadict['data'] = data 
129   json.dumps(datadict, ensure_ascii=False, indent="\t")
130   with open('your path and your json file name', 'w', encoding="utf-8") as make_file:
131      json.dump(datadict, make_file, ensure_ascii=False, indent='\t')
```

1. line 20
    - raw_data로 사용할 video가 있는 directory path로 변경
2. line 26
    - 이미지를 저장할 directory로 path를 변경
3. line 130
    - json을 저장할 path와 json명 설정

### to make json file

```python
$ cd preprocessing 
$ python generate_data.py
```

## References

- [https://github.com/qhan1028/Headpose-Detection](https://github.com/qhan1028/Headpose-Detection)
- [https://www.learnopencv.com/head-pose-estimation-using-opencv-and-dlib](https://www.learnopencv.com/head-pose-estimation-using-opencv-and-dlib) - headpose 원리
