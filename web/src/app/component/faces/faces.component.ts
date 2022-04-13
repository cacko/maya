import { Component, OnInit } from '@angular/core';
import {FaceService} from "../../service/face.service";

@Component({
  selector: 'app-faces',
  templateUrl: './faces.component.html',
  styleUrls: ['./faces.component.scss']
})
export class FacesComponent implements OnInit {

  loaded = false;

  constructor(
    public faces: FaceService
  ) { }

  ngOnInit(): void {
    this.faces.load().then(() => {
      this.loaded = true;
    });
  }

}
