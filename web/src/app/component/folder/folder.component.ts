import { Component, Input } from "@angular/core";
import { Router } from "@angular/router";
import { ImageService } from "../../service/image.service";
import { Folder } from "../../entity/folder";

@Component({
  selector: "app-folder",
  templateUrl: "./folder.component.html",
  styleUrls: ["./folder.component.scss"]
})
export class FolderComponent {


  @Input() folder?: Folder;

  constructor(
    private router: Router,
    private imageService: ImageService
  ) {
  }


  async onClick() {
    this.imageService.startLoader();
    await this.router.navigate(["_", this.folder?.name]);
  }
}
