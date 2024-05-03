import numpy as np
import wave


def calc_params(filename):
	file = wave.open(filename, mode="r")
	(nchannels, sampwidth, fs, nframes, _, _) = file.getparams()
	data = file.readframes(nframes)
	data = np.frombuffer(data, dtype={1: np.int8, 2: np.int16, 4: np.int32}[sampwidth])
	if nchannels != 1:
		data = np.sum(np.fromiter( (data[n::nchannels] for n in range(nchannels)), dtype=np.ndarray))
	data = np.trim_zeros(data/(256**sampwidth/2))
	sample50 = data[:round(0.05*fs)]
	M = sample50.size//2
	ACF = np.array([np.dot(sample50[:M+1], sample50[l:M+l+1]) for l in range(0, M+1)])
	sample = None
	peaks = np.where((ACF[1:-1] >= ACF[0:-2]) * (ACF[1:-1] >= ACF[2:]) * (ACF[1:-1] >= 0))[0] + 1
	F0 = fs/(peaks[np.where(ACF[peaks][1:-1] >= ACF[peaks][2:])[0] + 1][0] + 1) # частота основного тона
	ACF = None
	peaks = None
	Fc = 1.5*F0/fs  # частота среза
	H = lambda n: 2*Fc if n == 0 else np.sin(2*np.pi*Fc*n)/(np.pi*n)
	w = lambda n: 0.54 - 0.46*np.cos(2*np.pi*n/(N-1))
	N = 465
	h = np.array([H(n-(N-1)/2)*w(n) for n in range(0, N)])
	Fc = None
	H = None
	w = None
	filter_data = np.convolve(data, h, 'same')[round((N-1)/2):]
	h = None
	N = None
	In = np.where((filter_data[0:-2] > 0) * (filter_data[1:-1] <= 0))[0]
	Nc = In.size
	filter_data = None
	boof_In = None
	PERC = 0.15
	P = np.zeros(Nc-1, dtype=np.int64)
	F = np.zeros(Nc-2)
	P[0] = In[0] + np.argmin(data[In[0]:In[1]-1])
	ERR = lambda i, j: 1/(j-P[i-1]) * np.sum([(data[k + j - P[i-1]] - data[k])**2 for k in range(P[i-1], j)])

	for i in range(1, Nc-1):
		P[i] = In[i] + (P[i-1] - In[i-1])
		J1 = P[i] - round(PERC*(P[i] - P[i-1]))
		J2 = P[i] + round(PERC*(P[i] - P[i-1]))

		while True:

			Jm = J1
			min_err = np.inf

			for j in range(J1, J2+1):
				boof_err = ERR(i, j)
				if boof_err < min_err:
					min_err = boof_err
					Jm = j

			if Jm == J1:
				J1 -= round(0.5*(J2-J1))
			elif Jm == J2:
				J2 += round(0.5*(J2-J1))
			else:
				break

		P[i] = Jm
		delta = - 0.5*(ERR(i, Jm+1) - ERR(i, Jm-1))/(ERR(i, Jm+1) - 2*ERR(i, Jm) + ERR(i, Jm-1))
		F[i-1] = fs/(P[i] - P[i-1] + delta)

	In = None
	PERC = None
	ERR = None
	J1 = None
	J2 = None
	Jm = None
	min_err = None
	boof_err = None
	delta = None
	std_F = np.std(F)
	T = 1/F
	N = Nc-1
	full_A = np.array([np.abs(np.max(data[P[i-1]:P[i]]) - np.min(data[P[i-1]:P[i]])) for i in range(1, N)])
	Nc = None
	Jloc = N/(N-1) * np.sum(np.abs( np.subtract(T[:-1], T[1:]) ))/np.sum(np.abs( T )) * 100
	Sloc = N/(N-1) * np.sum(np.abs( np.subtract(full_A[:-1], full_A[1:]) ))/np.sum(np.abs( full_A )) * 100
	T = None
	N = None
	full_A = None

	spectrum_A = np.abs(np.fft.fft(data))
	Formants = np.zeros(6)
	Formants[0] = F0
	F0_ind = F0*nframes/fs

	for i in range(1, 6):
		boof_interval = np.array([(i+5/6)*F0_ind, (i+7/6)*F0_ind]).astype(int)

		local_maximum = boof_interval[0] + np.argmax(spectrum_A[boof_interval[0]:boof_interval[1]])

		boof_interval = np.array([(i+2/3)*F0_ind, (i+4/3)*F0_ind]).astype(int)

		if local_maximum == boof_interval[0] + np.argmax(spectrum_A[boof_interval[0]:boof_interval[1]]):
			Formants[i] = fs*local_maximum/nframes

	spectrum_A = None
	F0_ind = None
	boof_interval = None
	local_maximum = None
	F0 = round(F0, ndigits=3)
	std_F = round(std_F, ndigits=3)
	Jloc = round(Jloc,ndigits=3)
	Sloc = round(Sloc, ndigits=3)

	for i in range(6):
		Formants[i] = round(Formants[i], ndigits=3)

	return F0, std_F,Jloc, Sloc

