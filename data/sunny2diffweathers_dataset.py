import os
from data.pix2pix_dataset import Pix2pixDataset



class Sunny2DiffWeathersDataset(Pix2pixDataset):

    @staticmethod
    def modify_commandline_options(parser, is_train):
        parser = Pix2pixDataset.modify_commandline_options(parser, is_train)
        parser.add_argument('--test_mode', type=str, default='all',
                            help='specify style mode to control multi-modal image synthesis (MMIS) during test phase:'
                                 'night | cloudy | rainy | snowy | all')
        parser.set_defaults(preprocess_mode='fixed')
        parser.set_defaults(load_size=512)
        parser.set_defaults(crop_size=512)
        parser.set_defaults(display_winsize=512)
        parser.set_defaults(aspect_ratio=2.0)
        opt, _ = parser.parse_known_args()
        if hasattr(opt, 'num_upsampling_layers'):
            parser.set_defaults(num_upsampling_layers='more')
        return parser

    def get_image_paths_recursive(self, folder_path):
        image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp'}
        image_paths = []

        for root, dirs, files in os.walk(folder_path):
            for file in files:
                _, ext = os.path.splitext(file)
                if ext.lower() in image_extensions:
                    full_path = os.path.join(root, file)
                    image_paths.append(os.path.abspath(full_path))
        return image_paths

    def get_paths(self, opt):
        croot = opt.croot
        sroot = opt.sroot
        ref_image = opt.s_image
        c_path = opt.c_path

        if c_path:
            c_image_paths = self.get_image_paths_recursive(c_path)
        else:
            with open(os.path.join(croot, 'bdd100k_lists/sunny2diffweathers/sunny_%s.txt' % opt.phase)) as c_list:
                c_image_paths_read = c_list.read().splitlines()
                c_image_paths = [os.path.join(croot, p) for p in c_image_paths_read if p != '']

        if opt.phase == 'train' or opt.test_mode == 'all':
            mode_list = ['night', 'cloudy', 'rainy', 'snowy']
        else:
            mode_list = [opt.test_mode]
        s_image_paths = []
        if ref_image:
            s_image_paths = [ref_image for _ in range(len(c_image_paths))]
        else:
            for mode in mode_list:
                with open(os.path.join(sroot, 'bdd100k_lists/sunny2diffweathers/%s_%s.txt' % (mode, opt.phase))) as s_list:
                    s_image_paths_read = s_list.read().splitlines()
                    s_image_paths_mode = [os.path.join(sroot, p) for p in s_image_paths_read if p != '']
                s_image_paths.extend(s_image_paths_mode)

            while len(s_image_paths) < len(c_image_paths):
                s_image_paths = s_image_paths + s_image_paths

        instance_paths = []

        length = min(len(c_image_paths), len(s_image_paths))
        c_image_paths = c_image_paths[:length]
        s_image_paths = s_image_paths[:length]
        return c_image_paths, s_image_paths, instance_paths

    def paths_match(self, path1, path2):
        return True