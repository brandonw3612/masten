import argparse

import torch
import diffusion.linearized as dl

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--model', type=str, required=True)
    parser.add_argument('--steps', type=int, default=10)
    parser.add_argument('--batch-size', type=int, default=10)
    parser.add_argument('--temperature', type=float, default=1.0)
    args = parser.parse_args()

    device = torch.accelerator.current_accelerator()
    print('Using torch device: ', device)

    g = dl.inference(args.model, device, steps=args.steps, batch_size=args.batch_size, temperature=args.temperature)
    valid, othto, noeos = 0, 0, 0
    for i, prog in enumerate(g):
        if '<EOS>' in prog:
            eos_pos = prog.index('<EOS>')
            pads = set(prog[eos_pos + 1:])
            if len(pads) == 0 or (len(pads) == 1 and '<PAD>' in pads):
                comment = ''
                valid += 1
            else:
                comment = f' (Invalid token after EOS: {[t for t in pads if t != "<PAD>"]})'
                othto += 1
            prog = prog[:eos_pos]
        else:
            comment = ' (No EOS)'
            noeos += 1
        print(f"Generated Program {i + 1}: {str.join(' ', prog)}{comment}")
    print(f"Valid: {valid} / Other Tokens: {othto} / No EOS: {noeos}")