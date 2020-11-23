import React, { Component } from 'react';
import ImageUploader from 'react-images-upload';
// import Axios from 'axios';
var axios = require('axios');

class Detection extends Component {
 
  constructor(props) {
    super(props);
    this.state = { pictures: [] };
    this.onDrop = this.onDrop.bind(this);
    this.uploadImage = this.uploadImage.bind(this);
  }

  onDrop(picture) {
    this.setState({
        pictures: this.state.pictures.concat(picture),
    });
  }

  // url = 'https://cpzo2024o2.execute-api.eu-west-3.amazonaws.com/dev/upload';

  uploadImage(){
    console.log(this.state.pictures)
  }

  render(){
    return (
      <>
        <div className='detection'>
          <h1>Anatomical Stages Radiography Detection</h1>
        </div>
        <div className='App-content'>
          <ImageUploader
            key="image-uploader"
            withIcon={true}
            singleImage={true}
            withPreview={true}
            withLabel={true}
            label="Maximum size file: 5MB | Accepted format [jpg-jpeg-png]"
            buttonText="Choose an image"
            // onChange={props.onImage}
            imgExtension={['.jpg', '.png', '.jpeg']}
            maxFileSize={5242880}
            fileSizeError=" file size is too big"
            fileTypeError="is not supported file extension"
          ></ImageUploader>
          <button>Run detection</button>
        </div>
        
      </>
    );
  }
}
export default Detection;