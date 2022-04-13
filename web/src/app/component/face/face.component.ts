import {Component, Input, OnInit} from '@angular/core';
import {FaceEntity} from "../../entity/face";

@Component({
  selector: 'app-face',
  templateUrl: './face.component.html',
  styleUrls: ['./face.component.scss']
})
export class FaceComponent implements OnInit{

  @Input() face: FaceEntity|null = null;

  link = "";

  constructor() { }


  getImageStyle(): { [key: string]: string } {
    return {
      'background-image': `url("data:image/webp;base64,${this.face?.image}")`,
    };
  }

  ngOnInit(): void {
    this.link = `/face/${this.face?.name}`;
  }

}
