subjects=( 1 )  #  e.g. subjects=( 1 2 5 6 7 10 )
subj_arg="${subjects[@]}" # stringify it

#games=( 'vgfmri3_chase' 'vgfmri3_helper' 'vgfmri3_bait' 'vgfmri3_lemmings' 'vgfmri3_plaqueAttack' 'vgfmri3_zelda')
#games=( 'vgfmri3_chase' 'vgfmri3_lemmings' 'vgfmri3_plaqueAttack' )
games=('vgfmri3_chase')

source activate pedro

for subj in ${subjects[*]}; do
    for game in ${games[*]}; do
        python fmri_makeMovie.py ${subj} ${game}
    done
done
