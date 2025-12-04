import argparse
import random

import diffusion.linearized as dl


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--dataset', type=str, required=True)
    args = parser.parse_args()

    dataset = dl.LinearizedDataset.from_checkpoint(args.dataset)
    samples = dataset.samples

    print(f'Vocabulary: {dataset.tokenizer.vocab}')
    while True:
        random.shuffle(samples)
        for i in range(10):
            decoded = dataset.tokenizer.decode(samples[i].tolist())
            eos_pos = decoded.index('<EOS>')
            print(str.join(' ', decoded[:eos_pos]))
        inp = input("Press Enter to see more samples or type 'x' to quit: ")
        if inp == 'x':
            break