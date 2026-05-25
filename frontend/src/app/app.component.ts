import { HttpClient } from '@angular/common/http';
import { Component } from '@angular/core';
type Stage = 'upload' | 'action' | 'encode' | 'decode' | 'result_decode' |'result_encode';
@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrl: './app.component.scss',
})
export class AppComponent {
  imgSrc = '';
  file!: File;
  stage: Stage = 'upload';
  msg='';
  production_api = "https://dimtrakon.pythonanywhere.com"
  dev_api = "/api"
  production_flag = true;
  loading= false;

  constructor(private http: HttpClient) {}

  reset() {
    this.stage = 'upload';
    this.imgSrc = '';
    this.file = undefined as any;
    this.msg = '';
  }

  fileSelected(e: any) {
    this.file = e.target.files[0];
    const url = window.URL.createObjectURL(this.file);
    this.imgSrc = url;
  }

  uploadFile() {
    if (!!this.file) {
      const formData = new FormData();
      formData.append('file', this.file);
      this.loading = true;
      this.http.post(`${this.production_flag?this.production_api:this.dev_api}/upload`, formData).subscribe((json: any) => {
        if (json['status'] == 'ok') {
          this.stage = 'action';
        }
        this.loading = false;
      });
    }
  }

  reciveFile() {
    this.http
      .get(`${this.production_flag?this.production_api:this.dev_api}/get-file`, {
        responseType: 'blob',
      })
      .subscribe((blob) => {
        const url = window.URL.createObjectURL(blob);
        this.imgSrc = url;
      });
  }

  download() {
    const link = document.createElement('a');
    link.href = this.imgSrc;
    link.download = 'img.png';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  }

  moveToEncode(){
    this.stage = 'encode'
  }

  moveToDecode(){
    this.stage = 'decode'
  }

  decodeStageLSB(){
    this.stage = 'decode';
    this.decodeFile();
  }

  decodeStagePVD(){
    this.stage = 'decode';
    this.decodeFilePVD();
  }

  decodeStageDCT(){
    this.stage = 'decode';
    this.decodeFileDCT();
  }

  decodeFile() {
    this.loading = true;
    this.http.get(`${this.production_flag?this.production_api:this.dev_api}/decode`).subscribe((json:any) => {
      this.msg = json["message"];
      this.loading = false;
      this.stage = "result_decode"
    });
  }

  decodeFilePVD() {
    this.loading = true;
    this.http.get(`${this.production_flag?this.production_api:this.dev_api}/decode-pvd`).subscribe((json:any) => {
      this.msg = json["message"];
      this.loading = false;
      this.stage = "result_decode"
    });
  }

  decodeFileDCT() {
    this.loading = true;
    this.http.get(`${this.production_flag?this.production_api:this.dev_api}/decode-dct`).subscribe((json:any) => {
      this.msg = json["message"];
      this.loading = false;
      this.stage = "result_decode"
    });
  }

  encodeFile() {
    let inputMsg = <HTMLInputElement>document.getElementById('msg');
    if (!!inputMsg && !!inputMsg.value) {
      let msg = inputMsg.value;
      this.loading = true;
      this.http
        .get(`${this.production_flag?this.production_api:this.dev_api}/encode`, {
          params: {
            msg,
          },
        })
        .subscribe((json: any) => {
          if (json['status'] == 'ok') {
            this.reciveFile();
            this.stage = "result_encode";
          }
          this.loading = false;
        });
    }
  }

  encodeFilePVD() {
    let inputMsg = <HTMLInputElement>document.getElementById('msg');
    if (!!inputMsg && !!inputMsg.value) {
      let msg = inputMsg.value;
      this.loading = true;
      this.http
        .get(`${this.production_flag?this.production_api:this.dev_api}/encode-pvd`, {
          params: {
            msg,
          },
        })
        .subscribe((json: any) => {
          if (json['status'] == 'ok') {
            this.reciveFile();
            this.stage = "result_encode";
          }
          this.loading = false;
        }, (error: any) => {
          this.msg = error?.error?.message || 'PVD encode failed';
          this.stage = 'result_decode';
          this.loading = false;
        });
    }
  }

  encodeFileDCT() {
    let inputMsg = <HTMLInputElement>document.getElementById('msg');
    if (!!inputMsg && !!inputMsg.value) {
      let msg = inputMsg.value;
      this.loading = true;
      this.http
        .get(`${this.production_flag?this.production_api:this.dev_api}/encode-dct`, {
          params: {
            msg,
          },
        })
        .subscribe((json: any) => {
          if (json['status'] == 'ok') {
            this.reciveFile();
            this.stage = "result_encode";
          }
          this.loading = false;
        });
    }
  }

  getMessageBasedOnStage(){
    if(this.stage == 'upload'){
      return 'Upload a file to start'
    }else if(this.stage == 'action'){
      return 'Choose an action to continue'
    }else if(this.stage == 'encode'){
      return 'Write your message and encode'
    }else if ( this.stage == 'result_encode'){
      return 'Download your image'
    }else if(this.stage == 'result_decode'){
      return 'Your message is'
    }else if(this.stage == 'decode'){
      return 'Choose a method to decode the image'
    }
    return ''
  }
}
